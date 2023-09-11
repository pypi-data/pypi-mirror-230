// Defines fileno on msys:
#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#include <cstddef>
#include <cstdint>
#include <cstdio>
#endif

#include "ggml.h"
#include "llama-ggml.h"
#include "llama-util.h"
#ifdef GGML_USE_CUBLAS
#include "ggml-cuda.h"
#elif defined(GGML_USE_CLBLAST)
#include "ggml-opencl.h"
#endif

#ifdef GGML_USE_METAL
#include "ggml-metal.h"
#endif
#ifdef GGML_USE_MPI
#include "ggml-mpi.h"
#endif
#ifdef GGML_USE_K_QUANTS
#ifndef QK_K
#ifdef GGML_QKK_64
#define QK_K 64
#else
#define QK_K 256
#endif
#endif
#endif

#include <algorithm>
#include <array>
#include <atomic>
#include <cassert>
#include <cinttypes>
#include <climits>
#include <cstring>
#include <ctime>
#include <fstream>
#include <initializer_list>
#include <map>
#include <memory>
#include <mutex>
#include <numeric>
#include <queue>
#include <random>
#include <sstream>
#include <thread>
#include <unordered_map>

#if defined(_MSC_VER)
#pragma warning(disable : 4244 4267)  // possible loss of data
#endif

#if !defined(GGML_USE_CUBLAS) && !defined(GGML_USE_METAL)
#include "ggml-alloc.h"
#define LLAMA_USE_ALLOCATOR
#else
#define LLAMA_USE_SCRATCH
#define LLAMA_MAX_SCRATCH_BUFFERS 16
#endif

namespace llama_ggml {

// available llama models
enum e_model {
  MODEL_UNKNOWN,
  MODEL_3B,
  MODEL_7B,
  MODEL_13B,
  MODEL_30B,
  MODEL_65B,
  MODEL_70B,
};

static const size_t kB = 1024;
static const size_t MB = 1024 * 1024;

// computed for n_ctx == 2048
// TODO: dynamically determine these sizes
//       needs modifications in ggml

typedef void (*offload_func_t)(struct ggml_tensor *tensor);

void llama_nop(struct ggml_tensor *tensor) {  // don't offload by default
  (void)tensor;
}

//
// memory sizes (calculated for n_batch == 512)
//

static const std::map<e_model, size_t> &MEM_REQ_SCRATCH0(int n_ctx) {
  static std::map<e_model, size_t> k_sizes = {
      {MODEL_3B, ((size_t)n_ctx / 16ull + 92ull) * MB},
      {MODEL_7B, ((size_t)n_ctx / 16ull + 100ull) * MB},
      {MODEL_13B, ((size_t)n_ctx / 12ull + 120ull) * MB},
      {MODEL_30B, ((size_t)n_ctx / 9ull + 160ull) * MB},
      {MODEL_65B, ((size_t)n_ctx / 6ull + 256ull) * MB},  // guess
      {MODEL_70B, ((size_t)n_ctx / 7ull + 164ull) * MB},
  };
  return k_sizes;
}

static const std::map<e_model, size_t> &MEM_REQ_SCRATCH1() {
  static std::map<e_model, size_t> k_sizes = {
      {MODEL_3B, 128ull * MB},  {MODEL_7B, 160ull * MB},
      {MODEL_13B, 192ull * MB}, {MODEL_30B, 256ull * MB},
      {MODEL_65B, 384ull * MB},  // guess
      {MODEL_70B, 304ull * MB},
  };
  return k_sizes;
}

// used to store the compute graph tensors + non-scratch data
static const std::map<e_model, size_t> &MEM_REQ_EVAL() {
  static std::map<e_model, size_t> k_sizes = {
      {MODEL_3B, 8ull * MB},   {MODEL_7B, 10ull * MB},  {MODEL_13B, 12ull * MB},
      {MODEL_30B, 16ull * MB}, {MODEL_65B, 24ull * MB},  // guess
      {MODEL_70B, 24ull * MB},
  };
  return k_sizes;
}

// amount of VRAM needed per batch size to hold temporary results
// the values for 3b and 65b are not derived from testing but instead chosen
// conservatively
static const std::map<e_model, size_t> &VRAM_REQ_SCRATCH_BASE() {
  static std::map<e_model, size_t> k_sizes = {
      {MODEL_3B, 512ull * kB},
      {MODEL_7B, 512ull * kB},
      {MODEL_13B, 640ull * kB},
      {MODEL_30B, 768ull * kB},
      {MODEL_65B, 1536ull * kB},
      {MODEL_70B, 1536ull * kB},  // TODO (likely can be reduced)
  };
  return k_sizes;
}

// amount of VRAM needed per batch size and context to hold temporary results
// the values for 3b and 65b are not derived from testing but instead chosen
// conservatively
static const std::map<e_model, size_t> &VRAM_REQ_SCRATCH_PER_CONTEXT() {
  static std::map<e_model, size_t> k_sizes = {
      {MODEL_3B, 128ull},  {MODEL_7B, 128ull},
      {MODEL_13B, 160ull}, {MODEL_30B, 208ull},
      {MODEL_65B, 416ull}, {MODEL_70B, 416ull},  // TODO (likely can be reduced)
  };
  return k_sizes;
}

// default hparams (LLaMA 7B)
struct llama_hparams {
  uint32_t n_vocab = 32000;
  uint32_t n_ctx = 512;  // this is provided as user input?
  uint32_t n_embd = 4096;
  uint32_t n_mult = 256;
  uint32_t n_head = 32;
  uint32_t n_head_kv = 32;
  uint32_t n_layer = 32;
  uint32_t n_rot = 64;

  // LLaMAv2
  // TODO: load from model data hparams
  float f_ffn_mult = 1.0f;
  float f_rms_norm_eps = LLAMA_DEFAULT_RMS_EPS;

  float rope_freq_base = 10000.0f;
  float rope_freq_scale = 1.0f;

  enum llama_ftype ftype = LLAMA_FTYPE_MOSTLY_F16;

  bool operator!=(const llama_hparams &other) const {
    return static_cast<bool>(
        memcmp(this, &other, sizeof(llama_hparams)));  // NOLINT
  }

  uint32_t n_gqa() const { return n_head / n_head_kv; }

  uint32_t n_embd_head() const { return n_embd / n_head; }

  uint32_t n_embd_gqa() const { return n_embd / n_gqa(); }

  size_t kv_size() const {
    size_t result = 2ull;
    result *= (size_t)n_embd_gqa();
    result *= (size_t)n_ctx;
    result *= (size_t)n_layer;
    result *= sizeof(ggml_fp16_t);
    return result;
  }
};

struct llama_layer {
  // normalization
  struct ggml_tensor *attention_norm;

  // attention
  struct ggml_tensor *wq;
  struct ggml_tensor *wk;
  struct ggml_tensor *wv;
  struct ggml_tensor *wo;

  // normalization
  struct ggml_tensor *ffn_norm;

  // ff
  struct ggml_tensor *w1;
  struct ggml_tensor *w2;
  struct ggml_tensor *w3;
};

struct llama_kv_cache {
  struct ggml_tensor *k = NULL;
  struct ggml_tensor *v = NULL;

  struct ggml_context *ctx = NULL;

  llama_ctx_buffer buf;

  int n;  // number of tokens currently in the cache

  ~llama_kv_cache() {
    if (ctx) {
      ggml_free(ctx);
    }

#ifdef GGML_USE_CUBLAS
    ggml_cuda_free_data(k);
    ggml_cuda_free_data(v);
#endif  // GGML_USE_CUBLAS
  }
};

struct llama_vocab {
  using id = int32_t;
  using token = std::string;

  struct token_score {
    token tok;
    float score;
  };

  std::unordered_map<token, id> token_to_id;
  std::vector<token_score> id_to_token;
};

struct llama_model {
  e_model type = MODEL_UNKNOWN;

  llama_hparams hparams;

  struct ggml_tensor *tok_embeddings;

  struct ggml_tensor *norm;
  struct ggml_tensor *output;

  std::vector<llama_layer> layers;
  int n_gpu_layers;

  // context
  struct ggml_context *ctx = NULL;

  // the model memory buffer
  llama_ctx_buffer buf;

  // model memory mapped file
  std::unique_ptr<llama_mmap> mapping;

  // objects representing data potentially being locked in memory
  llama_mlock mlock_buf;
  llama_mlock mlock_mmap;

  // for quantize-stats only
  std::vector<std::pair<std::string, struct ggml_tensor *>> tensors_by_name;

  int64_t t_load_us = 0;
  int64_t t_start_us = 0;

  llama_vocab vocab;

  ~llama_model() {
    if (ctx) {
      ggml_free(ctx);
    }

#ifdef GGML_USE_CUBLAS
    for (size_t i = 0; i < tensors_by_name.size(); ++i) {
      ggml_cuda_free_data(tensors_by_name[i].second);
    }
    ggml_cuda_free_scratch();
#elif defined(GGML_USE_CLBLAST)
    for (size_t i = 0; i < tensors_by_name.size(); ++i) {
      ggml_cl_free_data(tensors_by_name[i].second);
    }
#endif
  }
};

struct llama_context {
  llama_context(const llama_model &model)
      : model(model),
        t_load_us(model.t_load_us),
        t_start_us(model.t_start_us) {}
  ~llama_context() {
    if (model_owner) {
      delete &model;
    }
#ifdef GGML_USE_METAL
    if (ctx_metal) {
      ggml_metal_free(ctx_metal);
    }
#endif
#ifdef LLAMA_USE_ALLOCATOR
    if (alloc) {
      ggml_allocr_free(alloc);
    }
#endif
  }

  std::mt19937 rng;

  bool has_evaluated_once = false;

  int64_t t_sample_us = 0;
  int64_t t_eval_us = 0;
  int64_t t_p_eval_us = 0;

  int32_t n_sample = 0;  // number of tokens sampled
  int32_t n_eval = 0;    // number of eval calls
  int32_t n_p_eval =
      0;  // number of tokens in eval calls for the prompt (with batch size > 1)

  const llama_model &model;

  bool model_owner = false;

  int64_t t_load_us;
  int64_t t_start_us;

  // key + value cache for the self attention
  struct llama_kv_cache kv_self;

  size_t mem_per_token = 0;

  // decode output (2-dimensional array: [n_tokens][n_vocab])
  std::vector<float> logits;
  bool logits_all = false;

  // input embedding (1-dimensional array: [n_embd])
  std::vector<float> embedding;

  // reusable buffer for `struct ggml_graph_plan.work_data`
  std::vector<uint8_t> work_buffer;

  // memory buffers used to evaluate the model
  // TODO: move in llama_state
  llama_ctx_buffer buf_compute;

#ifdef LLAMA_USE_ALLOCATOR
  llama_ctx_buffer buf_alloc;
  ggml_allocr *alloc = NULL;
#endif

#ifdef LLAMA_USE_SCRATCH
  llama_ctx_buffer buf_scratch[LLAMA_MAX_SCRATCH_BUFFERS];
  int buf_last = 0;
  size_t buf_max_size[LLAMA_MAX_SCRATCH_BUFFERS] = {0};
#endif

#ifdef GGML_USE_METAL
  ggml_metal_context *ctx_metal = NULL;
#endif

#ifdef GGML_USE_MPI
  ggml_mpi_context *ctx_mpi = NULL;
#endif

  void use_buf(struct ggml_context *ctx, int i) {
#if defined(LLAMA_USE_SCRATCH)
    size_t last_size = 0;

    if (i == -1) {
      last_size = ggml_set_scratch(ctx, {
                                            0,
                                            0,
                                            nullptr,
                                        });
    } else {
      auto &buf = buf_scratch[i];
      last_size = ggml_set_scratch(ctx, {
                                            0,
                                            buf.size,
                                            buf.addr,
                                        });
    }

    if (buf_last >= 0) {
      buf_max_size[buf_last] = std::max(buf_max_size[buf_last], last_size);
    }

    buf_last = i;
#else
    (void)i;
    (void)ctx;
#endif
  }

  size_t get_buf_max_mem(int i) const {
#if defined(LLAMA_USE_SCRATCH)
    return buf_max_size[i];
#else
    (void)i;
    return 0;
#endif
  }
};

template <typename T>
static T checked_mul(T a, T b) {
  T ret = a * b;
  if (a != 0 && ret / a != b) {
    throw std::runtime_error(format("overflow multiplying %llu * %llu",
                                    (unsigned long long)a,
                                    (unsigned long long)b));
  }
  return ret;
}

static size_t checked_div(size_t a, size_t b) {
  if (b == 0 || a % b != 0) {
    throw std::runtime_error(format("error dividing %zu / %zu", a, b));
  }
  return a / b;
}

static std::string llama_format_tensor_shape(const std::vector<uint32_t> &ne) {
  char buf[256];
  snprintf(buf, sizeof(buf), "%5u", ne.at(0));
  for (size_t i = 1; i < ne.size(); i++) {
    snprintf(buf + strlen(buf), sizeof(buf) - strlen(buf), " x %5u", ne.at(i));
  }
  return buf;
}

static size_t llama_calc_tensor_size(const std::vector<uint32_t> &ne,
                                     enum ggml_type type) {
  size_t size = ggml_type_size(type);
  for (uint32_t dim : ne) {
    size = checked_mul<size_t>(size, dim);
  }
  return size / ggml_blck_size(type);
}

struct llama_load_tensor {
  std::string name;
  enum ggml_type type = GGML_TYPE_F32;
  std::vector<uint32_t> ne;
  size_t file_off;
  size_t size;
  struct ggml_tensor *ggml_tensor = NULL;
  uint8_t *data;
};

struct llama_load_tensors_map {
  // tensors is kept in a separate vector to preserve file order
  std::vector<llama_load_tensor> tensors;
  std::unordered_map<std::string, size_t> name_to_idx;
};

enum llama_file_version {
  LLAMA_FILE_VERSION_GGML,
  LLAMA_FILE_VERSION_GGMF_V1,  // added version field and scores in vocab
  LLAMA_FILE_VERSION_GGJT_V1,  // added padding
  LLAMA_FILE_VERSION_GGJT_V2,  // changed quantization format
  LLAMA_FILE_VERSION_GGJT_V3,  // changed Q4 and Q8 quantization format
};

struct llama_file_loader {
  llama_file file;
  llama_file_version file_version;
  llama_hparams hparams;
  llama_vocab vocab;

  llama_file_loader(const char *fname, llama_load_tensors_map &tensors_map)
      : file(fname, "rb") {
    read_magic();
    read_hparams();
    read_vocab();
    read_tensor_metadata(tensors_map);
  }
  void read_magic() {
    uint32_t magic = file.read_u32();

    if (magic == LLAMA_FILE_MAGIC_GGML) {
      file_version = LLAMA_FILE_VERSION_GGML;
      return;
    }

    uint32_t version = file.read_u32();

    switch (magic) {
      case LLAMA_FILE_MAGIC_GGMF:
        switch (version) {
          case 1:
            file_version = LLAMA_FILE_VERSION_GGMF_V1;
            return;
        }
        break;
      case LLAMA_FILE_MAGIC_GGJT:
        switch (version) {
          case 1:
            file_version = LLAMA_FILE_VERSION_GGJT_V1;
            return;
          case 2:
            file_version = LLAMA_FILE_VERSION_GGJT_V2;
            return;
          case 3:
            file_version = LLAMA_FILE_VERSION_GGJT_V3;
            return;
        }
    }

    throw std::runtime_error(
        format("unknown (magic, version) combination: %08x, %08x; is this "
               "really a GGML file?",
               magic, version));
  }
  void read_hparams() {
    hparams.n_vocab = file.read_u32();
    hparams.n_embd = file.read_u32();
    hparams.n_mult = file.read_u32();
    hparams.n_head = file.read_u32();
    hparams.n_layer = file.read_u32();
    hparams.n_rot = file.read_u32();
    hparams.ftype = (enum llama_ftype)file.read_u32();

    // LLaMAv2
    // TODO: read from header
    hparams.n_head_kv = hparams.n_head;
  }
  void read_vocab() {
    vocab.id_to_token.resize(hparams.n_vocab);

    for (uint32_t i = 0; i < hparams.n_vocab; i++) {
      uint32_t len = file.read_u32();
      std::string word = file.read_string(len);

      float score = 0.0f;
      file.read_raw(&score, sizeof(score));

      vocab.token_to_id[word] = i;

      auto &tok_score = vocab.id_to_token[i];
      tok_score.tok = std::move(word);
      tok_score.score = score;
    }
  }
  void read_tensor_metadata(llama_load_tensors_map &tensors_map) {
    while (file.tell() < file.size) {
      llama_load_tensor tensor;
      uint32_t n_dims = file.read_u32();
      uint32_t name_len = file.read_u32();
      tensor.type = (enum ggml_type)file.read_u32();
      tensor.ne.resize(n_dims);
      file.read_raw(tensor.ne.data(), sizeof(tensor.ne[0]) * n_dims);
      std::string name = file.read_string(name_len);
      if (n_dims < 1 || n_dims > 2) {
        throw std::runtime_error(
            format("llama.cpp: tensor '%s' should not be %u-dimensional",
                   name.c_str(), n_dims));
      }
      switch (tensor.type) {
        case GGML_TYPE_F32:
        case GGML_TYPE_F16:
        case GGML_TYPE_Q4_0:
        case GGML_TYPE_Q4_1:
        case GGML_TYPE_Q5_0:
        case GGML_TYPE_Q5_1:
        case GGML_TYPE_Q8_0:
        case GGML_TYPE_Q2_K:
        case GGML_TYPE_Q3_K:
        case GGML_TYPE_Q4_K:
        case GGML_TYPE_Q5_K:
        case GGML_TYPE_Q6_K:
          break;
        default: {
          throw std::runtime_error(
              format("unrecognized tensor type %u\n", tensor.type));
        }
      }

      // skip to the next multiple of 32 bytes
      if (file_version >= LLAMA_FILE_VERSION_GGJT_V1) {
        file.seek(-static_cast<ptrdiff_t>(file.tell()) & 31, SEEK_CUR);
      }

      tensor.file_off = file.tell();
      tensor.name = name;
      tensor.size = llama_calc_tensor_size(tensor.ne, tensor.type);
      file.seek(tensor.size, SEEK_CUR);

      tensors_map.tensors.push_back(tensor);
      tensors_map.name_to_idx[name] = tensors_map.tensors.size() - 1;
    }
  }
};

struct llama_file_saver {
  llama_file file;
  llama_file_loader *any_file_loader;
  llama_file_saver(const char *fname, llama_file_loader *any_file_loader,
                   enum llama_ftype new_ftype)
      : file(fname, "wb"), any_file_loader(any_file_loader) {
    write_magic();
    write_hparams(new_ftype);
    write_vocab();
  }
  void write_magic() {
    file.write_u32(LLAMA_FILE_MAGIC);    // magic
    file.write_u32(LLAMA_FILE_VERSION);  // version
  }
  void write_hparams(enum llama_ftype new_ftype) {
    const llama_hparams &hparams = any_file_loader->hparams;
    file.write_u32(hparams.n_vocab);
    file.write_u32(hparams.n_embd);
    file.write_u32(hparams.n_mult);
    file.write_u32(hparams.n_head);
    file.write_u32(hparams.n_layer);
    file.write_u32(hparams.n_rot);
    file.write_u32(new_ftype);
  }
  void write_vocab() {
    if (any_file_loader->file_version == LLAMA_FILE_VERSION_GGML) {
      fprintf(stderr,
              "llama.cpp: WARNING: input is an old file that doesn't have "
              "scores; will add dummy scores\n");
    }
    uint32_t n_vocab = any_file_loader->hparams.n_vocab;
    for (uint32_t i = 0; i < n_vocab; i++) {
      const auto &token_score = any_file_loader->vocab.id_to_token.at(i);
      file.write_u32((uint32_t)token_score.tok.size());
      file.write_raw(token_score.tok.data(), token_score.tok.size());
      file.write_raw(&token_score.score, sizeof(token_score.score));
    }
  }
  void write_tensor(llama_load_tensor &tensor, enum ggml_type new_type,
                    const void *new_data, size_t new_size) {
    switch (new_type) {
      case GGML_TYPE_F32:
      case GGML_TYPE_F16:
      case GGML_TYPE_Q4_0:
      case GGML_TYPE_Q4_1:
      case GGML_TYPE_Q5_0:
      case GGML_TYPE_Q5_1:
      case GGML_TYPE_Q8_0:
      case GGML_TYPE_Q2_K:
      case GGML_TYPE_Q3_K:
      case GGML_TYPE_Q4_K:
      case GGML_TYPE_Q5_K:
      case GGML_TYPE_Q6_K:
        break;
      default:
        LLAMA_ASSERT(false);
    }
    file.write_u32((uint32_t)tensor.ne.size());
    file.write_u32((uint32_t)tensor.name.size());
    file.write_u32(new_type);
    file.write_raw(tensor.ne.data(), sizeof(tensor.ne[0]) * tensor.ne.size());
    file.write_raw(tensor.name.data(), tensor.name.size());
    file.seek(-static_cast<ptrdiff_t>(file.tell()) & 31, SEEK_CUR);
    LLAMA_ASSERT(new_size == llama_calc_tensor_size(tensor.ne, new_type));
    file.write_raw(new_data, new_size);
  }
};

struct llama_model_loader {
  std::unique_ptr<llama_file_loader> file_loader;
  llama_load_tensors_map tensors_map;
  bool use_mmap;
  size_t num_ggml_tensors_created = 0;
  struct ggml_context *ggml_ctx = NULL;
  std::unique_ptr<llama_mmap> mapping;

  llama_model_loader(const std::string &fname_base, bool use_mmap) {
    file_loader = std::unique_ptr<llama_file_loader>(
        new llama_file_loader(fname_base.c_str(), tensors_map));
    if (!llama_mmap::SUPPORTED) {
      use_mmap = false;
    }
    this->use_mmap = use_mmap;
  }

  void calc_sizes(size_t *ctx_size_p, size_t *mmapped_size_p) const {
    *ctx_size_p = *mmapped_size_p = 0;
    for (const llama_load_tensor &lt : tensors_map.tensors) {
      *ctx_size_p += sizeof(struct ggml_tensor) + GGML_OBJECT_SIZE;
      *(use_mmap ? mmapped_size_p : ctx_size_p) += lt.size + 16;
    }
  }

  struct ggml_tensor *get_tensor(const std::string &name,
                                 const std::vector<uint32_t> &ne,
                                 ggml_backend backend) {
    auto it = tensors_map.name_to_idx.find(name);
    if (it == tensors_map.name_to_idx.end()) {
      throw std::runtime_error(std::runtime_error(format(
          "llama.cpp: tensor '%s' is missing from model", name.c_str())));
    }
    llama_load_tensor &lt = tensors_map.tensors.at(it->second);
    if (lt.ne != ne) {
      throw std::runtime_error(
          format("llama.cpp: tensor '%s' has wrong shape; expected %s, got %s",
                 name.c_str(), llama_format_tensor_shape(ne).c_str(),
                 llama_format_tensor_shape(lt.ne).c_str()));
    }

    return get_tensor_for(lt, backend);
  }

  struct ggml_tensor *get_tensor_for(llama_load_tensor &lt,
                                     ggml_backend backend) {
    struct ggml_tensor *tensor;
    if (backend != GGML_BACKEND_CPU) {
      ggml_set_no_alloc(ggml_ctx, true);
    }
    if (lt.ne.size() == 2) {
      tensor = ggml_new_tensor_2d(ggml_ctx, lt.type, lt.ne.at(0), lt.ne.at(1));
    } else {
      LLAMA_ASSERT(lt.ne.size() == 1);
      tensor = ggml_new_tensor_1d(ggml_ctx, lt.type, lt.ne.at(0));
    }
    ggml_set_name(tensor, lt.name.c_str());
    LLAMA_ASSERT(
        lt.ggml_tensor ==
        NULL);  // if this fails, we called get_tensor twice on the same tensor

    if (backend != GGML_BACKEND_CPU) {
      ggml_set_no_alloc(ggml_ctx, use_mmap);
    }
    tensor->backend = backend;
    lt.ggml_tensor = tensor;
    num_ggml_tensors_created++;
    return tensor;
  }

  void done_getting_tensors() const {
    if (num_ggml_tensors_created != tensors_map.tensors.size()) {
      throw std::runtime_error(
          std::string("llama.cpp: file contained more tensors than expected"));
    }
  }

  void load_all_data(llama_progress_callback progress_callback,
                     void *progress_callback_user_data, llama_mlock *lmlock) {
    size_t data_size = 0;
    size_t prefetch_size = 0;
    size_t lock_size = 0;
    for (const llama_load_tensor &lt : tensors_map.tensors) {
      data_size += lt.size;
      if (lt.ggml_tensor->backend == GGML_BACKEND_CPU) {
        prefetch_size += lt.size;
      }
    }

    if (use_mmap) {
      mapping.reset(
          new llama_mmap(&file_loader->file, prefetch_size, ggml_is_numa()));
      if (lmlock) {
        lmlock->init(mapping->addr);
      }
    }

    size_t done_size = 0;
    for (llama_load_tensor &lt : tensors_map.tensors) {
      if (progress_callback) {
        progress_callback((float)done_size / data_size,
                          progress_callback_user_data);
      }
      LLAMA_ASSERT(lt.ggml_tensor);  // unused tensors should have been caught
                                     // by load_data already
      lt.data = (uint8_t *)lt.ggml_tensor->data;

      // allocate temp buffer if not using mmap
      if (!use_mmap && lt.data == NULL) {
        GGML_ASSERT(lt.ggml_tensor->backend != GGML_BACKEND_CPU);
        lt.data = (uint8_t *)malloc(ggml_nbytes(lt.ggml_tensor));
      }

      load_data_for(lt);

      switch (lt.ggml_tensor->backend) {
        case GGML_BACKEND_CPU:
          lt.ggml_tensor->data = lt.data;
          if (use_mmap && lmlock) {
            lock_size += lt.size;
            lmlock->grow_to(lock_size);
          }
          break;
#if defined(GGML_USE_CUBLAS)
        case GGML_BACKEND_GPU:
        case GGML_BACKEND_GPU_SPLIT:
          ggml_cuda_transform_tensor(lt.data, lt.ggml_tensor);
          if (!use_mmap) {
            free(lt.data);
          }
          break;
#elif defined(GGML_USE_CLBLAST)
        case GGML_BACKEND_GPU:
          ggml_cl_transform_tensor(lt.data, lt.ggml_tensor);
          if (!use_mmap) {
            free(lt.data);
          }
          break;
#endif
        default:
          continue;
      }

      done_size += lt.size;
    }
  }

  void load_data_for(llama_load_tensor &lt) {
    if (use_mmap) {
      lt.data = (uint8_t *)mapping->addr + lt.file_off;
    } else {
      llama_file &file = file_loader->file;
      file.seek(lt.file_off, SEEK_SET);
      file.read_raw(lt.data, lt.size);
    }

    if (0) {
      print_checksum(lt);
    }
  }

  static void print_checksum(llama_load_tensor &lt) {
    uint32_t sum = 0;
    for (size_t i = 0; i < lt.size; i++) {
      uint8_t byte = lt.data[i];
      sum = byte + (sum << 6) + (sum << 16) - sum;  // sdbm hash
    }
    fprintf(stderr, "%s checksum: %#08x (%s, size %zu)\n", lt.name.c_str(), sum,
            llama_format_tensor_shape(lt.ne).c_str(), lt.size);
  }
};

//
// kv cache
//

static bool kv_cache_init(const struct llama_hparams &hparams,
                          struct llama_kv_cache &cache, ggml_type wtype,
                          int n_ctx, int n_gpu_layers) {
  const int n_embd = hparams.n_embd_gqa();
  const int n_layer = hparams.n_layer;

  const int64_t n_mem = n_layer * n_ctx;
  const int64_t n_elements = n_embd * n_mem;

  cache.buf.resize(2u * n_elements * ggml_type_size(wtype) + 2u * MB);
  cache.n = 0;

  struct ggml_init_params params;
  params.mem_size = cache.buf.size;
  params.mem_buffer = cache.buf.addr;
  params.no_alloc = false;

  cache.ctx = ggml_init(params);

  if (!cache.ctx) {
    fprintf(stderr, "%s: failed to allocate memory for kv cache\n", __func__);
    return false;
  }

  cache.k = ggml_new_tensor_1d(cache.ctx, wtype, n_elements);
  cache.v = ggml_new_tensor_1d(cache.ctx, wtype, n_elements);
  ggml_set_name(cache.k, "cache_k");
  ggml_set_name(cache.v, "cache_v");

  (void)n_gpu_layers;
#ifdef GGML_USE_CUBLAS
  if (n_gpu_layers > n_layer + 1) {
    ggml_cuda_assign_buffers_no_scratch(cache.v);
  }
  if (n_gpu_layers > n_layer + 2) {
    ggml_cuda_assign_buffers_no_scratch(cache.k);
  }
#endif  // GGML_USE_CUBLAS

  return true;
}

struct llama_context_params llama_context_default_params() {
  struct llama_context_params result = {
      /*.seed                        =*/LLAMA_DEFAULT_SEED,
      /*.n_ctx                       =*/512,
      /*.n_batch                     =*/512,
      /*.n_gqa                       =*/1,
      /*.rms_norm_eps                =*/LLAMA_DEFAULT_RMS_EPS,
      /*.gpu_layers                  =*/0,
      /*.main_gpu                    =*/0,
      /*.tensor_split                =*/nullptr,
      /*.rope_freq_base              =*/10000.0f,
      /*.rope_freq_scale             =*/1.0f,
      /*.progress_callback           =*/nullptr,
      /*.progress_callback_user_data =*/nullptr,
      /*.low_vram                    =*/false,
      /*.mul_mat_q                   =*/false,
      /*.f16_kv                      =*/true,
      /*.logits_all                  =*/false,
      /*.vocab_only                  =*/false,
      /*.use_mmap                    =*/true,
      /*.use_mlock                   =*/false,
      /*.embedding                   =*/false,
  };

  return result;
}

struct llama_model_quantize_params llama_model_quantize_default_params() {
  struct llama_model_quantize_params result = {
      /*.nthread                     =*/0,
      /*.ftype                       =*/LLAMA_FTYPE_MOSTLY_Q5_1,
      /*.allow_requantize            =*/false,
      /*.quantize_output_tensor      =*/true,
  };

  return result;
}

int llama_max_devices() { return LLAMA_MAX_DEVICES; }

bool llama_mmap_supported() { return llama_mmap::SUPPORTED; }

bool llama_mlock_supported() { return llama_mlock::SUPPORTED; }

void llama_backend_init(bool numa) {
  ggml_time_init();

  // needed to initialize f16 tables
  {
    struct ggml_init_params params = {0, NULL, false};
    struct ggml_context *ctx = ggml_init(params);
    ggml_free(ctx);
  }

  if (numa) {
    ggml_numa_init();
  }

#ifdef GGML_USE_MPI
  ggml_mpi_backend_init();
#endif
}

void llama_backend_free() {
#ifdef GGML_USE_MPI
  ggml_mpi_backend_free();
#endif
}

int64_t llama_time_us() { return ggml_time_us(); }

//
// model loading
//

static const char *llama_file_version_name(llama_file_version version) {
  switch (version) {
    case LLAMA_FILE_VERSION_GGML:
      return "'ggml' (old version with low tokenizer quality and no mmap "
             "support)";
    case LLAMA_FILE_VERSION_GGMF_V1:
      return "ggmf v1 (old version with no mmap support)";
    case LLAMA_FILE_VERSION_GGJT_V1:
      return "ggjt v1 (pre #1405)";
    case LLAMA_FILE_VERSION_GGJT_V2:
      return "ggjt v2 (pre #1508)";
    case LLAMA_FILE_VERSION_GGJT_V3:
      return "ggjt v3 (latest)";
  }

  return "unknown";
}

static const char *llama_ftype_name(enum llama_ftype ftype) {
  switch (ftype) {
    case LLAMA_FTYPE_ALL_F32:
      return "all F32";
    case LLAMA_FTYPE_MOSTLY_F16:
      return "mostly F16";
    case LLAMA_FTYPE_MOSTLY_Q4_0:
      return "mostly Q4_0";
    case LLAMA_FTYPE_MOSTLY_Q4_1:
      return "mostly Q4_1";
    case LLAMA_FTYPE_MOSTLY_Q4_1_SOME_F16:
      return "mostly Q4_1, some F16";
    case LLAMA_FTYPE_MOSTLY_Q5_0:
      return "mostly Q5_0";
    case LLAMA_FTYPE_MOSTLY_Q5_1:
      return "mostly Q5_1";
    case LLAMA_FTYPE_MOSTLY_Q8_0:
      return "mostly Q8_0";
    // K-quants
    case LLAMA_FTYPE_MOSTLY_Q2_K:
      return "mostly Q2_K";
    case LLAMA_FTYPE_MOSTLY_Q3_K_S:
      return "mostly Q3_K - Small";
    case LLAMA_FTYPE_MOSTLY_Q3_K_M:
      return "mostly Q3_K - Medium";
    case LLAMA_FTYPE_MOSTLY_Q3_K_L:
      return "mostly Q3_K - Large";
    case LLAMA_FTYPE_MOSTLY_Q4_K_S:
      return "mostly Q4_K - Small";
    case LLAMA_FTYPE_MOSTLY_Q4_K_M:
      return "mostly Q4_K - Medium";
    case LLAMA_FTYPE_MOSTLY_Q5_K_S:
      return "mostly Q5_K - Small";
    case LLAMA_FTYPE_MOSTLY_Q5_K_M:
      return "mostly Q5_K - Medium";
    case LLAMA_FTYPE_MOSTLY_Q6_K:
      return "mostly Q6_K";
    default:
      return "unknown, may not work";
  }
}

static const char *llama_model_type_name(e_model type) {
  switch (type) {
    case MODEL_3B:
      return "3B";
    case MODEL_7B:
      return "7B";
    case MODEL_13B:
      return "13B";
    case MODEL_30B:
      return "30B";
    case MODEL_65B:
      return "65B";
    case MODEL_70B:
      return "70B";
    default:
      LLAMA_ASSERT(false);
  }
}

static void llama_model_load_internal(
    const std::string &fname, llama_model &model, llama_vocab &vocab, int n_ctx,
    int n_batch, int n_gqa, float rms_norm_eps, int n_gpu_layers, int main_gpu,
    const float *tensor_split, const bool mul_mat_q, float rope_freq_base,
    float rope_freq_scale, bool low_vram, ggml_type memory_type, bool use_mmap,
    bool use_mlock, bool vocab_only, llama_progress_callback progress_callback,
    void *progress_callback_user_data) {
  model.t_start_us = ggml_time_us();

  std::unique_ptr<llama_model_loader> ml(
      new llama_model_loader(fname, use_mmap));

  vocab = std::move(ml->file_loader->vocab);
  model.hparams = ml->file_loader->hparams;
  model.n_gpu_layers = n_gpu_layers;
  llama_file_version file_version = ml->file_loader->file_version;

  auto &hparams = model.hparams;

  // TODO: read from file
  hparams.f_rms_norm_eps = rms_norm_eps;

  {
    switch (hparams.n_layer) {
      case 26:
        model.type = e_model::MODEL_3B;
        break;
      case 32:
        model.type = e_model::MODEL_7B;
        break;
      case 40:
        model.type = e_model::MODEL_13B;
        break;
      case 60:
        model.type = e_model::MODEL_30B;
        break;
      case 80:
        model.type = e_model::MODEL_65B;
        break;
      default: {
        if (hparams.n_layer < 32) {
          model.type = e_model::MODEL_7B;
        }
      } break;
    }

    hparams.n_ctx = n_ctx;

    // LLaMAv2
    // TODO: temporary until GGUF
    LLAMA_ASSERT(hparams.n_head % n_gqa == 0);
    hparams.n_head_kv = hparams.n_head / n_gqa;
    if (model.type == e_model::MODEL_65B && n_gqa == 8) {
      model.type = e_model::MODEL_70B;
      hparams.f_ffn_mult = 1.3f;  // from the params.json of the 70B model
    }

    hparams.rope_freq_base = rope_freq_base;
    hparams.rope_freq_scale = rope_freq_scale;
  }

  // ref:
  // https://github.com/facebookresearch/llama/blob/6c7fe276574e78057f917549435a2554000a876d/llama/model.py#L194-L199
  const uint32_t n_ff_raw = 2 * (4 * hparams.n_embd) / 3;
  const uint32_t n_ff_mult = hparams.f_ffn_mult * n_ff_raw;
  const uint32_t n_ff =
      ((n_ff_mult + hparams.n_mult - 1) / hparams.n_mult) * hparams.n_mult;
  // const uint32_t n_ff = 28672;

  if (file_version < LLAMA_FILE_VERSION_GGJT_V2) {
    if (hparams.ftype != LLAMA_FTYPE_ALL_F32 &&
        hparams.ftype != LLAMA_FTYPE_MOSTLY_F16 &&
        hparams.ftype != LLAMA_FTYPE_MOSTLY_Q8_0) {
      throw std::runtime_error(
          format("this format is no longer supported (see "
                 "https://github.com/ggerganov/llama.cpp/pull/1405)"));
    }
  }

  if (file_version < LLAMA_FILE_VERSION_GGJT_V3) {
    if (hparams.ftype == LLAMA_FTYPE_MOSTLY_Q4_0 ||
        hparams.ftype == LLAMA_FTYPE_MOSTLY_Q4_1 ||
        hparams.ftype == LLAMA_FTYPE_MOSTLY_Q8_0) {
      throw std::runtime_error(
          format("this format is no longer supported (see "
                 "https://github.com/ggerganov/llama.cpp/pull/1508)"));
    }
  }

  if (vocab_only) {
    return;
  }

  auto &ctx = model.ctx;

  size_t ctx_size;
  size_t mmapped_size;
  ml->calc_sizes(&ctx_size, &mmapped_size);

  // create the ggml context
  {
    model.buf.resize(ctx_size);
    if (use_mlock) {
      model.mlock_buf.init(model.buf.addr);
      model.mlock_buf.grow_to(model.buf.size);
    }

    struct ggml_init_params params = {
        /*.mem_size   =*/model.buf.size,
        /*.mem_buffer =*/model.buf.addr,
        /*.no_alloc   =*/ml->use_mmap,
    };

    model.ctx = ggml_init(params);
    if (!model.ctx) {
      throw std::runtime_error(format("ggml_init() failed"));
    }
  }

  (void)main_gpu;
  (void)mul_mat_q;
#if defined(GGML_USE_CUBLAS)
  ggml_cuda_set_main_device(main_gpu);
  ggml_cuda_set_mul_mat_q(mul_mat_q);
#define LLAMA_BACKEND_OFFLOAD GGML_BACKEND_GPU
#define LLAMA_BACKEND_OFFLOAD_SPLIT GGML_BACKEND_GPU_SPLIT
#elif defined(GGML_USE_CLBLAST)
#define LLAMA_BACKEND_OFFLOAD GGML_BACKEND_GPU
#define LLAMA_BACKEND_OFFLOAD_SPLIT GGML_BACKEND_GPU
#else
#define LLAMA_BACKEND_OFFLOAD GGML_BACKEND_CPU
#define LLAMA_BACKEND_OFFLOAD_SPLIT GGML_BACKEND_CPU
#endif

  // prepare memory for the weights
  size_t vram_weights = 0;
  size_t vram_scratch = 0;
  {
    const uint32_t n_embd = hparams.n_embd;
    const uint32_t n_embd_gqa = hparams.n_embd_gqa();
    const uint32_t n_layer = hparams.n_layer;
    const uint32_t n_vocab = hparams.n_vocab;

    ml->ggml_ctx = ctx;

    model.tok_embeddings = ml->get_tensor("tok_embeddings.weight",
                                          {n_embd, n_vocab}, GGML_BACKEND_CPU);

    // "output" tensor
    {
      ggml_backend backend_norm;
      ggml_backend backend_output;
      if (n_gpu_layers > int(n_layer)) {  // NOLINT
        // norm is not performance relevant on its own but keeping it in VRAM
        // reduces data copying on Windows however this is detrimental unless
        // everything is on the GPU
#ifndef _WIN32
        backend_norm = low_vram ? GGML_BACKEND_CPU : LLAMA_BACKEND_OFFLOAD;
#else
        backend_norm = low_vram || n_gpu_layers <= (int)n_layer + 2
                           ? GGML_BACKEND_CPU
                           : LLAMA_BACKEND_OFFLOAD;
#endif  // _WIN32

        backend_output = LLAMA_BACKEND_OFFLOAD_SPLIT;
      } else {
        backend_norm = GGML_BACKEND_CPU;
        backend_output = GGML_BACKEND_CPU;
      }

      model.norm = ml->get_tensor("norm.weight", {n_embd}, backend_norm);
      model.output =
          ml->get_tensor("output.weight", {n_embd, n_vocab}, backend_output);
      if (backend_norm == GGML_BACKEND_GPU) {
        vram_weights += ggml_nbytes(model.norm);
      }
      if (backend_output == GGML_BACKEND_GPU_SPLIT) {
        vram_weights += ggml_nbytes(model.output);
      }
    }

    const int i_gpu_start = n_layer - n_gpu_layers;

    model.layers.resize(n_layer);
    for (uint32_t i = 0; i < n_layer; ++i) {
      const ggml_backend backend = int(i) < i_gpu_start
                                       ? GGML_BACKEND_CPU
                                       : LLAMA_BACKEND_OFFLOAD;  // NOLINT
      const ggml_backend backend_split =
          int(i) < i_gpu_start ? GGML_BACKEND_CPU
                               : LLAMA_BACKEND_OFFLOAD_SPLIT;  // NOLINT

      auto &layer = model.layers[i];

      std::string layers_i = "layers." + std::to_string(i);

      layer.attention_norm = ml->get_tensor(layers_i + ".attention_norm.weight",
                                            {n_embd}, backend);

      layer.wq = ml->get_tensor(layers_i + ".attention.wq.weight",
                                {n_embd, n_embd}, backend_split);
      layer.wk = ml->get_tensor(layers_i + ".attention.wk.weight",
                                {n_embd, n_embd_gqa}, backend_split);
      layer.wv = ml->get_tensor(layers_i + ".attention.wv.weight",
                                {n_embd, n_embd_gqa}, backend_split);
      layer.wo = ml->get_tensor(layers_i + ".attention.wo.weight",
                                {n_embd, n_embd}, backend_split);

      layer.ffn_norm =
          ml->get_tensor(layers_i + ".ffn_norm.weight", {n_embd}, backend);

      layer.w1 = ml->get_tensor(layers_i + ".feed_forward.w1.weight",
                                {n_embd, n_ff}, backend_split);
      layer.w2 = ml->get_tensor(layers_i + ".feed_forward.w2.weight",
                                {n_ff, n_embd}, backend_split);
      layer.w3 = ml->get_tensor(layers_i + ".feed_forward.w3.weight",
                                {n_embd, n_ff}, backend_split);

      if (backend == GGML_BACKEND_GPU) {
        vram_weights += ggml_nbytes(layer.attention_norm) +
                        ggml_nbytes(layer.wq) + ggml_nbytes(layer.wk) +
                        ggml_nbytes(layer.wv) + ggml_nbytes(layer.wo) +
                        ggml_nbytes(layer.ffn_norm) + ggml_nbytes(layer.w1) +
                        ggml_nbytes(layer.w2) + ggml_nbytes(layer.w3);
      }
    }
  }

  ml->done_getting_tensors();

  // print memory requirements
  {
    const size_t scale = memory_type == GGML_TYPE_F32 ? 2 : 1;

    // this is the total memory required to run the inference
    size_t mem_required = ctx_size + mmapped_size -
                          vram_weights;  // weights in VRAM not in memory

#ifndef LLAMA_USE_ALLOCATOR
    mem_required += MEM_REQ_SCRATCH0(hparams.n_ctx).at(model.type) +
                    MEM_REQ_SCRATCH1().at(model.type) +
                    MEM_REQ_EVAL().at(model.type);
#endif

    // this is the memory required by one llama_state
    const size_t mem_required_state = scale * hparams.kv_size();

    (void)vram_scratch;
    (void)n_batch;
#ifdef GGML_USE_CUBLAS
    if (low_vram) {
      fprintf(
          stderr,
          "%s: not allocating a VRAM scratch buffer due to low VRAM option\n",
          __func__);
      ggml_cuda_set_scratch_size(0);  // disable scratch
    } else {
      const size_t vram_scratch_base = VRAM_REQ_SCRATCH_BASE().at(model.type);
      const size_t vram_scratch_per_context =
          VRAM_REQ_SCRATCH_PER_CONTEXT().at(model.type);
      vram_scratch =
          n_batch * (vram_scratch_base + n_ctx * vram_scratch_per_context);
      ggml_cuda_set_scratch_size(vram_scratch);
    }
#endif  // GGML_USE_CUBLAS

#if defined(GGML_USE_CUBLAS) || defined(GGML_USE_CLBLAST)
    const int n_gpu = std::min(n_gpu_layers, int(hparams.n_layer));
    size_t vram_kv_cache = 0;

#ifdef GGML_USE_CUBLAS
    const int max_backend_supported_layers = hparams.n_layer + 3;
    const int max_offloadable_layers =
        low_vram ? hparams.n_layer + 1 : hparams.n_layer + 3;
    if (n_gpu_layers > (int)hparams.n_layer + 1) {
      if (low_vram) {
        fprintf(stderr,
                "%s: cannot offload v cache to GPU due to low VRAM option\n",
                __func__);
      } else {
        vram_kv_cache += hparams.kv_size() / 2;
      }
    }
    if (n_gpu_layers > (int)hparams.n_layer + 2) {
      if (low_vram) {
        fprintf(stderr,
                "%s: cannot offload k cache to GPU due to low VRAM option\n",
                __func__);
      } else {
        vram_kv_cache += hparams.kv_size() / 2;
      }
    }
#elif defined(GGML_USE_CLBLAST)
    const int max_backend_supported_layers = hparams.n_layer + 1;
    const int max_offloadable_layers = hparams.n_layer + 1;
#endif  // GGML_USE_CUBLAS

#else
    (void)n_gpu_layers;
#endif  // defined(GGML_USE_CUBLAS) || defined(GGML_USE_CLBLAST)
  }

  // populate `tensors_by_name`
  for (llama_load_tensor &lt : ml->tensors_map.tensors) {
    model.tensors_by_name.emplace_back(lt.name, lt.ggml_tensor);
  }

  (void)tensor_split;
#if defined(GGML_USE_CUBLAS)
  { ggml_cuda_set_tensor_split(tensor_split); }
#endif

  ml->load_all_data(progress_callback, progress_callback_user_data,
                    use_mlock ? &model.mlock_mmap : NULL);

  if (progress_callback) {
    progress_callback(1.0f, progress_callback_user_data);
  }

  model.mapping = std::move(ml->mapping);

  // loading time will be recalculate after the first eval, so
  // we take page faults deferred by mmap() into consideration
  model.t_load_us = ggml_time_us() - model.t_start_us;
}

static bool llama_model_load(
    const std::string &fname, llama_model &model, llama_vocab &vocab, int n_ctx,
    int n_batch, int n_gqa, float rms_norm_eps, int n_gpu_layers, int main_gpu,
    const float *tensor_split, const bool mul_mat_q, float rope_freq_base,
    float rope_freq_scale, bool low_vram, ggml_type memory_type, bool use_mmap,
    bool use_mlock, bool vocab_only, llama_progress_callback progress_callback,
    void *progress_callback_user_data) {
  try {
    llama_model_load_internal(
        fname, model, vocab, n_ctx, n_batch, n_gqa, rms_norm_eps, n_gpu_layers,
        main_gpu, tensor_split, mul_mat_q, rope_freq_base, rope_freq_scale,
        low_vram, memory_type, use_mmap, use_mlock, vocab_only,
        progress_callback, progress_callback_user_data);
    return true;
  } catch (const std::exception &err) {
    fprintf(stderr, "error loading model: %s\n", err.what());
    return false;
  }
}

static struct ggml_cgraph *llama_build_graph(llama_context &lctx,
                                             const llama_token *tokens,
                                             const float *embd, int n_tokens,
                                             int n_past) {
  LLAMA_ASSERT((!tokens && embd) || (tokens && !embd));

  const int N = n_tokens;

  const auto &model = lctx.model;
  const auto &hparams = model.hparams;

  const auto &kv_self = lctx.kv_self;

  LLAMA_ASSERT(!!kv_self.ctx);

  const int64_t n_embd = hparams.n_embd;
  const int64_t n_layer = hparams.n_layer;
  const int64_t n_ctx = hparams.n_ctx;
  const int64_t n_head = hparams.n_head;
  const int64_t n_head_kv = hparams.n_head_kv;
  const int64_t n_embd_head = hparams.n_embd_head();
  const int64_t n_embd_gqa = hparams.n_embd_gqa();

  LLAMA_ASSERT(n_embd_head == hparams.n_rot);

  const float freq_base = hparams.rope_freq_base;
  const float freq_scale = hparams.rope_freq_scale;
  const float rms_norm_eps = hparams.f_rms_norm_eps;

  const int n_gpu_layers = model.n_gpu_layers;

  auto &mem_per_token = lctx.mem_per_token;
  auto &buf_compute = lctx.buf_compute;

  struct ggml_init_params params = {
      /*.mem_size   =*/buf_compute.size,
      /*.mem_buffer =*/buf_compute.addr,
      /*.no_alloc   =*/false,
  };

#ifdef LLAMA_USE_ALLOCATOR
  params.no_alloc = true;
#endif

  struct ggml_context *ctx0 = ggml_init(params);

  ggml_cgraph *gf = ggml_new_graph(ctx0);

  struct ggml_tensor *cur;
  struct ggml_tensor *inpL;

  if (tokens) {
    struct ggml_tensor *inp_tokens = ggml_new_tensor_1d(ctx0, GGML_TYPE_I32, N);

#ifdef LLAMA_USE_ALLOCATOR
    ggml_allocr_alloc(lctx.alloc, inp_tokens);
    if (!ggml_allocr_is_measure(lctx.alloc)) {
      memcpy(inp_tokens->data, tokens, N * ggml_element_size(inp_tokens));
    }
#else
    memcpy(inp_tokens->data, tokens, N * ggml_element_size(inp_tokens));
#endif
    ggml_set_name(inp_tokens, "inp_tokens");

    inpL = ggml_get_rows(ctx0, model.tok_embeddings, inp_tokens);
  } else {
#ifdef GGML_USE_MPI
    GGML_ASSERT(false && "not implemented");
#endif

    inpL = ggml_new_tensor_2d(ctx0, GGML_TYPE_F32, n_embd, N);

#ifdef LLAMA_USE_ALLOCATOR
    ggml_allocr_alloc(lctx.alloc, inpL);
    if (!ggml_allocr_is_measure(lctx.alloc)) {
      memcpy(inpL->data, embd, N * n_embd * ggml_element_size(inpL));
    }
#else
    memcpy(inpL->data, embd, N * n_embd * ggml_element_size(inpL));
#endif
  }

  const int i_gpu_start = n_layer - n_gpu_layers;
  (void)i_gpu_start;

  // offload functions set the tensor output backend to GPU
  // tensors are GPU-accelerated if any input or the output has been offloaded
  //
  // with the low VRAM option VRAM scratch is disabled in
  // llama_load_model_internal in that case ggml_cuda_assign_buffers has no
  // effect
  offload_func_t offload_func_nr = llama_nop;  // nr = non-repeating
  offload_func_t offload_func_kq = llama_nop;
  offload_func_t offload_func_v = llama_nop;

#ifdef GGML_USE_CUBLAS
  if (n_gpu_layers > n_layer) {
    offload_func_nr = ggml_cuda_assign_buffers;
  }
  if (n_gpu_layers > n_layer + 1) {
    offload_func_v = ggml_cuda_assign_buffers;
  }
  if (n_gpu_layers > n_layer + 2) {
    offload_func_kq = ggml_cuda_assign_buffers;
  }
#endif  // GGML_USE_CUBLAS

  struct ggml_tensor *KQ_scale = ggml_new_tensor_1d(ctx0, GGML_TYPE_F32, 1);
#ifdef LLAMA_USE_ALLOCATOR
  ggml_allocr_alloc(lctx.alloc, KQ_scale);
  if (!ggml_allocr_is_measure(lctx.alloc)) {
    ggml_set_f32(KQ_scale, 1.0f / sqrtf(float(n_embd) / n_head));
  }
#else
  ggml_set_f32(KQ_scale, 1.0f / sqrtf(float(n_embd) / n_head));
#endif
  ggml_set_name(KQ_scale, "1/sqrt(n_embd_head)");

  for (int il = 0; il < n_layer; ++il) {
    ggml_format_name(inpL, "layer_inp_%d", il);

    offload_func_t offload_func = llama_nop;

#ifdef GGML_USE_CUBLAS
    if (il >= i_gpu_start) {
      offload_func = ggml_cuda_assign_buffers;
    }
#endif  // GGML_USE_CUBLAS

    struct ggml_tensor *inpSA = inpL;

    lctx.use_buf(ctx0, 0);

    // norm
    {
      cur = ggml_rms_norm(ctx0, inpL, rms_norm_eps);
      offload_func(cur);
      ggml_set_name(cur, "rms_norm_0");

      // cur = cur*attention_norm(broadcasted)
      cur = ggml_mul(ctx0, cur, model.layers[il].attention_norm);
      offload_func(cur);
      ggml_set_name(cur, "attention_norm_0");
    }

    // self-attention
    {
      // compute Q and K and RoPE them
      struct ggml_tensor *tmpk = ggml_mul_mat(ctx0, model.layers[il].wk, cur);
      offload_func_kq(tmpk);
      ggml_set_name(tmpk, "tmpk");

      struct ggml_tensor *tmpq = ggml_mul_mat(ctx0, model.layers[il].wq, cur);
      offload_func_kq(tmpq);
      ggml_set_name(tmpq, "tmpq");

      struct ggml_tensor *Kcur = ggml_rope_custom_inplace(
          ctx0, ggml_reshape_3d(ctx0, tmpk, n_embd_head, n_head_kv, N), n_past,
          n_embd_head, 0, 0, freq_base, freq_scale);
      offload_func_kq(Kcur);
      ggml_set_name(Kcur, "Kcur");

      struct ggml_tensor *Qcur = ggml_rope_custom_inplace(
          ctx0, ggml_reshape_3d(ctx0, tmpq, n_embd_head, n_head, N), n_past,
          n_embd_head, 0, 0, freq_base, freq_scale);
      offload_func_kq(Qcur);
      ggml_set_name(Qcur, "Qcur");

      // store key and value to memory
      {
        // compute the transposed [N, n_embd] V matrix

        struct ggml_tensor *tmpv = ggml_mul_mat(ctx0, model.layers[il].wv, cur);
        offload_func_v(tmpv);
        ggml_set_name(tmpv, "tmpv");

        struct ggml_tensor *Vcur =
            ggml_transpose(ctx0, ggml_reshape_2d(ctx0, tmpv, n_embd_gqa, N));
        offload_func_v(Vcur);
        ggml_set_name(Vcur, "Vcur");

        struct ggml_tensor *k =
            ggml_view_1d(ctx0, kv_self.k, N * n_embd_gqa,
                         (ggml_element_size(kv_self.k) * n_embd_gqa) *
                             (il * n_ctx + n_past));
        offload_func_kq(k);
        ggml_set_name(k, "k");

        struct ggml_tensor *v = ggml_view_2d(
            ctx0, kv_self.v, N, n_embd_gqa,
            (n_ctx)*ggml_element_size(kv_self.v),
            (il * n_ctx) * ggml_element_size(kv_self.v) * n_embd_gqa +
                n_past * ggml_element_size(kv_self.v));
        offload_func_v(v);
        ggml_set_name(v, "v");

        // important: storing RoPE-ed version of K in the KV cache!
        ggml_build_forward_expand(gf, ggml_cpy(ctx0, Kcur, k));
        ggml_build_forward_expand(gf, ggml_cpy(ctx0, Vcur, v));
      }

      struct ggml_tensor *Q = ggml_permute(ctx0, Qcur, 0, 2, 1, 3);
      offload_func_kq(Q);
      ggml_set_name(Q, "Q");

      struct ggml_tensor *K = ggml_permute(
          ctx0,
          ggml_reshape_3d(
              ctx0,
              ggml_view_1d(
                  ctx0, kv_self.k, (n_past + N) * n_embd_gqa,
                  il * n_ctx * ggml_element_size(kv_self.k) * n_embd_gqa),
              n_embd_head, n_head_kv, n_past + N),
          0, 2, 1, 3);
      offload_func_kq(K);
      ggml_set_name(K, "K");

      // K * Q
      struct ggml_tensor *KQ = ggml_mul_mat(ctx0, K, Q);
      offload_func_kq(KQ);
      ggml_set_name(KQ, "KQ");

      // KQ_scaled = KQ / sqrt(n_embd_head)
      // KQ_scaled shape [n_past + N, N, n_head, 1]
      struct ggml_tensor *KQ_scaled = ggml_scale_inplace(ctx0, KQ, KQ_scale);
      offload_func_kq(KQ_scaled);
      ggml_set_name(KQ_scaled, "KQ_scaled");

      // KQ_masked = mask_past(KQ_scaled)
      struct ggml_tensor *KQ_masked =
          ggml_diag_mask_inf_inplace(ctx0, KQ_scaled, n_past);
      offload_func_kq(KQ_masked);
      ggml_set_name(KQ_masked, "KQ_masked");

      // KQ = soft_max(KQ_masked)
      struct ggml_tensor *KQ_soft_max = ggml_soft_max_inplace(ctx0, KQ_masked);
      offload_func_v(KQ_soft_max);
      ggml_set_name(KQ_soft_max, "KQ_soft_max");

      // split cached V into n_head heads
      struct ggml_tensor *V =
          ggml_view_3d(ctx0, kv_self.v, n_past + N, n_embd_head, n_head_kv,
                       n_ctx * ggml_element_size(kv_self.v),
                       n_ctx * ggml_element_size(kv_self.v) * n_embd_head,
                       n_ctx * ggml_element_size(kv_self.v) * n_embd_gqa * il);
      offload_func_v(V);
      ggml_set_name(V, "V");

#if 1
      struct ggml_tensor *KQV = ggml_mul_mat(ctx0, V, KQ_soft_max);
      offload_func_v(KQV);
      ggml_set_name(KQV, "KQV");
#else
      // make V contiguous in memory to speed up the matmul, however we waste
      // time on the copy on M1 this is faster for the perplexity computation,
      // but ~5% slower for the single-token generation is there a better way?
      struct ggml_tensor *V_cont =
          ggml_cpy(ctx0, V,
                   ggml_new_tensor_3d(ctx0, kv_self.v->type, n_past + N,
                                      n_embd_head, n_head));
      struct ggml_tensor *KQV = ggml_mul_mat(ctx0, V_cont, KQ_soft_max);
#endif

      // KQV_merged = KQV.permute(0, 2, 1, 3)
      struct ggml_tensor *KQV_merged = ggml_permute(ctx0, KQV, 0, 2, 1, 3);
      offload_func_v(KQV_merged);
      ggml_set_name(KQV_merged, "KQV_merged");

      // cur = KQV_merged.contiguous().view(n_embd, N)
      cur = ggml_cpy(ctx0, KQV_merged,
                     ggml_new_tensor_2d(ctx0, GGML_TYPE_F32, n_embd, N));
      offload_func_v(cur);
      ggml_set_name(cur, "KQV_merged_contiguous");

      // projection (no bias)
      cur = ggml_mul_mat(ctx0, model.layers[il].wo, cur);
      offload_func(cur);
      ggml_set_name(cur, "result_wo");
    }

    lctx.use_buf(ctx0, 1);

    struct ggml_tensor *inpFF = ggml_add(ctx0, cur, inpSA);
    offload_func(inpFF);
    ggml_set_name(inpFF, "inpFF");

    // feed-forward network
    {
      // norm
      {
        cur = ggml_rms_norm(ctx0, inpFF, rms_norm_eps);
        offload_func(cur);
        ggml_set_name(cur, "rms_norm_1");

        // cur = cur*ffn_norm(broadcasted)
        cur = ggml_mul(ctx0, cur, model.layers[il].ffn_norm);
        offload_func(cur);
        ggml_set_name(cur, "ffn_norm");
      }

      struct ggml_tensor *tmp = ggml_mul_mat(ctx0, model.layers[il].w3, cur);
      offload_func(tmp);
      ggml_set_name(tmp, "result_w3");

      cur = ggml_mul_mat(ctx0, model.layers[il].w1, cur);
      offload_func(cur);
      ggml_set_name(cur, "result_w1");

      // SILU activation
      cur = ggml_silu(ctx0, cur);
      offload_func(cur);
      ggml_set_name(cur, "silu");

      cur = ggml_mul(ctx0, cur, tmp);
      offload_func(cur);
      ggml_set_name(cur, "silu_x_result_w3");

      cur = ggml_mul_mat(ctx0, model.layers[il].w2, cur);
      offload_func(cur);
      ggml_set_name(cur, "result_w2");
    }

    cur = ggml_add(ctx0, cur, inpFF);
    offload_func(cur);
    ggml_set_name(cur, "inpFF_+_result_w2");

    // input for next layer
    inpL = cur;
  }

  lctx.use_buf(ctx0, 0);

  // norm
  {
    cur = ggml_rms_norm(ctx0, inpL, rms_norm_eps);
    offload_func_nr(cur);
    ggml_set_name(cur, "rms_norm_2");

    // cur = cur*norm(broadcasted)
    cur = ggml_mul(ctx0, cur, model.norm);
    // offload_func_nr(cur); // TODO CPU + GPU mirrored backend
    ggml_set_name(cur, "result_norm");
  }

  // lm_head
  cur = ggml_mul_mat(ctx0, model.output, cur);
  ggml_set_name(cur, "result_output");

  lctx.use_buf(ctx0, -1);

  // logits -> probs
  // cur = ggml_soft_max_inplace(ctx0, cur);

  ggml_build_forward_expand(gf, cur);

  if (mem_per_token == 0) {
    mem_per_token = ggml_used_mem(ctx0) / N;
  }

#if 0
    printf("\n%s: used_mem: eval ctx %.3f MB, scratch %.3f MB %.3f MB, work buf %.3f MB, n_past = %d, N = %d\n", __func__,
            ggml_used_mem(ctx0)/1024.0/1024.0,
            lctx.get_buf_max_mem(0)/1024.0/1024.0,
            lctx.get_buf_max_mem(1)/1024.0/1024.0,
            lctx.work_buffer.size()/1024.0/1024.0,
            n_past, N);
#endif

  ggml_free(ctx0);

  return gf;
}

// evaluate the transformer
//
//   - lctx:      llama context
//   - tokens:    new batch of tokens to process
//   - embd       embeddings input
//   - n_tokens   number of tokens
//   - n_past:    the context size so far
//   - n_threads: number of threads to use
//
static bool llama_eval_internal(llama_context &lctx, const llama_token *tokens,
                                const float *embd, int n_tokens, int n_past,
                                int n_threads, const char *cgraph_fname) {
  LLAMA_ASSERT((!tokens && embd) || (tokens && !embd));

  const int64_t t_start_us = ggml_time_us();

#ifdef GGML_USE_MPI
  ggml_mpi_eval_init(lctx.ctx_mpi, &n_tokens, &n_past, &n_threads);
#endif

  const int N = n_tokens;

  const auto &model = lctx.model;
  const auto &hparams = model.hparams;

  const auto &kv_self = lctx.kv_self;

  LLAMA_ASSERT(!!kv_self.ctx);

  const int64_t n_embd = hparams.n_embd;
  const int64_t n_vocab = hparams.n_vocab;

#ifdef LLAMA_USE_ALLOCATOR
  ggml_allocr_reset(lctx.alloc);
#endif

  ggml_cgraph *gf = llama_build_graph(lctx, tokens, embd, n_tokens, n_past);

#ifdef LLAMA_USE_ALLOCATOR
  ggml_allocr_alloc_graph(lctx.alloc, gf);
#endif

  // fprintf(stderr, "graph build time: %.3f ms (%d nodes, %d leafs)\n",
  // (ggml_time_us() - t_start_us)/1000.0, gf->n_nodes, gf->n_leafs);

  // for big prompts, if BLAS is enabled, it is better to use only one thread
  // otherwise, the threads are spin-lock waiting for the BLAS calls and are
  // degrading the performance
  n_threads =
      N >= 32 && ggml_cpu_has_blas() && !ggml_cpu_has_gpublas() ? 1 : n_threads;

  struct ggml_tensor *res = gf->nodes[gf->n_nodes - 1];
  struct ggml_tensor *embeddings = gf->nodes[gf->n_nodes - 2];

  LLAMA_ASSERT(strcmp(res->name, "result_output") == 0);
  LLAMA_ASSERT(strcmp(embeddings->name, "result_norm") == 0);

#if GGML_USE_MPI
  const int64_t n_layer = hparams.n_layer;
  ggml_mpi_graph_compute_pre(lctx.ctx_mpi, gf, n_layer);
#endif

#ifdef GGML_USE_METAL
  if (lctx.ctx_metal && N == 1) {
    // TODO: disabled until #2413 is resolved
    // if (!ggml_metal_if_optimized(lctx.ctx_metal)) {
    //    ggml_metal_graph_find_concurrency(lctx.ctx_metal, gf);
    //}
    ggml_metal_set_n_cb(lctx.ctx_metal, n_threads);
    ggml_metal_graph_compute(lctx.ctx_metal, gf);
    ggml_metal_get_tensor(lctx.ctx_metal, res);
    if (!lctx.embedding.empty()) {
      ggml_metal_get_tensor(lctx.ctx_metal, embeddings);
    }
  } else {
    // IMPORTANT:
    // Since we don't have efficient Matrix x Matrix Metal multiplication yet,
    // we fallback to vanilla ggml_graph_compute(). It uses Apple's Accelerate
    // CBLAS API which takes advantage of the ANE or the AMX coprocessor.
    //
    // When we implement Matrix x Matrix Metal multiplication, we can avoid this
    // branch. But for now, we have focused only on Matrix x Vector Metal
    // multiplication.
    //
    // TODO: avoid these syncs via shared memory (ref #1696)
    //
    if (lctx.ctx_metal) {
      // We need to sync the GPU KV cache with the CPU KV cache
      ggml_metal_get_tensor(lctx.ctx_metal, kv_self.k);
      ggml_metal_get_tensor(lctx.ctx_metal, kv_self.v);
    }

    ggml_graph_compute_helper(lctx.work_buffer, gf, n_threads);
  }
#else
  ggml_graph_compute_helper(lctx.work_buffer, gf, n_threads);
#endif

#if GGML_USE_MPI
  ggml_mpi_graph_compute_post(lctx.ctx_mpi, gf, n_layer);
#endif

  // update kv token count
  lctx.kv_self.n = n_past + N;

  if (cgraph_fname) {
    ggml_graph_export(gf, cgraph_fname);
  }

#ifdef GGML_PERF
  // print timing information per ggml operation (for debugging purposes)
  // requires GGML_PERF to be defined
  ggml_graph_print(gf);
#endif

  // plot the computation graph in dot format (for debugging purposes)
  // if (n_past%100 == 0) {
  //    ggml_graph_dump_dot(gf, NULL, "llama.dot");
  //}

  // extract logits
  {
    auto &logits_out = lctx.logits;

    if (lctx.logits_all) {
      logits_out.resize(n_vocab * N);
      memcpy(logits_out.data(), (float *)ggml_get_data(res),
             sizeof(float) * n_vocab * N);
    } else {
      // return result for just the last token
      logits_out.resize(n_vocab);
      memcpy(logits_out.data(),
             (float *)ggml_get_data(res) + (n_vocab * (N - 1)),
             sizeof(float) * n_vocab);
    }
  }

  // extract embeddings
  if (!lctx.embedding.empty()) {
    auto &embedding_out = lctx.embedding;

    embedding_out.resize(n_embd);
    memcpy(embedding_out.data(),
           (float *)ggml_get_data(embeddings) + (n_embd * (N - 1)),
           sizeof(float) * n_embd);
  }

  // measure the performance only for the single-token evals
  if (N == 1) {
    lctx.t_eval_us += ggml_time_us() - t_start_us;
    lctx.n_eval++;
  } else if (N > 1) {
    lctx.t_p_eval_us += ggml_time_us() - t_start_us;
    lctx.n_p_eval += N;
  }

  return true;
}

//
// tokenizer
//

static size_t utf8_len(char src) {
  const size_t lookup[] = {1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 3, 4};
  uint8_t highbits = static_cast<uint8_t>(src) >> 4;
  return lookup[highbits];
}

struct llama_sp_symbol {
  using index = int;
  index prev;
  index next;
  const char *text;
  size_t n;
};

static_assert(std::is_trivially_copyable<llama_sp_symbol>::value,
              "llama_sp_symbol is not trivially copyable");

struct llama_sp_bigram {
  struct comparator {
    bool operator()(llama_sp_bigram &l, llama_sp_bigram &r) {
      return (l.score < r.score) || (l.score == r.score && l.left > r.left);
    }
  };
  using queue_storage = std::vector<llama_sp_bigram>;
  using queue = std::priority_queue<llama_sp_bigram, queue_storage, comparator>;
  llama_sp_symbol::index left;
  llama_sp_symbol::index right;
  float score;
  size_t size;
};

// original implementation:
// https://github.com/ggerganov/llama.cpp/commit/074bea2eb1f1349a0118239c4152914aecaa1be4
struct llama_tokenizer {
  llama_tokenizer(const llama_vocab &vocab) : vocab_(vocab) {}

  void tokenize(const std::string &text, std::vector<llama_vocab::id> &output) {
    // split string into utf8 chars
    int index = 0;
    size_t offs = 0;
    while (offs < text.size()) {
      llama_sp_symbol sym;
      size_t char_len = std::min(text.size() - offs, utf8_len(text[offs]));
      sym.text = text.c_str() + offs;
      sym.n = char_len;
      offs += char_len;
      sym.prev = index - 1;
      sym.next = offs == text.size() ? -1 : index + 1;
      index++;
      symbols_.emplace_back(sym);
    }

    // seed the work queue with all possible 2-character tokens.
    for (size_t i = 1; i < symbols_.size(); ++i) {
      try_add_bigram(i - 1, i);
    }

    // keep substituting the highest frequency pairs for as long as we can.
    while (!work_queue_.empty()) {
      auto bigram = work_queue_.top();
      work_queue_.pop();

      auto &left_sym = symbols_[bigram.left];
      auto &right_sym = symbols_[bigram.right];

      // if one of the symbols already got merged, skip it.
      if (left_sym.n == 0 || right_sym.n == 0 ||
          left_sym.n + right_sym.n != bigram.size) {
        continue;
      }

      // merge the right sym into the left one
      left_sym.n += right_sym.n;
      right_sym.n = 0;

      // printf("left = '%*s' size = %zu\n", (int) left_sym.n, left_sym.text,
      // bigram.size);

      // remove the right sym from the chain
      left_sym.next = right_sym.next;
      if (right_sym.next >= 0) {
        symbols_[right_sym.next].prev = bigram.left;
      }

      // find more substitutions
      try_add_bigram(left_sym.prev, bigram.left);
      try_add_bigram(bigram.left, left_sym.next);
    }

    for (int i = 0; i != -1; i = symbols_[i].next) {
      auto &symbol = symbols_[i];
      auto token = vocab_.token_to_id.find(std::string(symbol.text, symbol.n));

      if (token == vocab_.token_to_id.end()) {
        // output any symbols that did not form tokens as bytes.
        for (int j = 0; j < (int)symbol.n; ++j) {
          // NOTE: old version, before #2420 - not sure what are the
          // implications of this
          // llama_vocab::id token_id = static_cast<uint8_t>(symbol.text[j]) +
          // 3;
          llama_vocab::id token_id =
              vocab_.token_to_id.at(std::string(1, symbol.text[j]));
          output.push_back(token_id);
        }
      } else {
        output.push_back((*token).second);
      }
    }
  }

 private:
  void try_add_bigram(int left, int right) {
    if (left == -1 || right == -1) {
      return;
    }

    const std::string text =
        std::string(symbols_[left].text, symbols_[left].n + symbols_[right].n);
    auto token = vocab_.token_to_id.find(text);

    if (token == vocab_.token_to_id.end()) {
      return;
    }

    if (static_cast<size_t>((*token).second) >= vocab_.id_to_token.size()) {
      return;
    }

    const auto &tok_score = vocab_.id_to_token[(*token).second];

    llama_sp_bigram bigram;
    bigram.left = left;
    bigram.right = right;
    bigram.score = tok_score.score;
    bigram.size = text.size();
    work_queue_.push(bigram);
  }

  const llama_vocab &vocab_;
  std::vector<llama_sp_symbol> symbols_;
  llama_sp_bigram::queue work_queue_;
};

static std::vector<llama_vocab::id> llama_tokenize(const llama_vocab &vocab,
                                                   const std::string &text,
                                                   bool bos) {
  llama_tokenizer tokenizer(vocab);
  std::vector<llama_vocab::id> output;

  if (text.empty()) {
    return output;
  }

  if (bos) {
    output.push_back(llama_token_bos());
  }

  tokenizer.tokenize(text, output);
  return output;
}

//
// grammar - internal
//

struct llama_grammar {
  const std::vector<std::vector<llama_grammar_element>> rules;
  std::vector<std::vector<const llama_grammar_element *>> stacks;
};

struct llama_grammar_candidate {
  size_t index;
  const uint32_t *code_points;
};

// NOTE: assumes valid utf8 (but checks for overrun)
// adds a terminating 0 for use as pointer
std::vector<uint32_t> decode_utf8(const char *src) {
  static const int lookup[] = {1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 3, 4};
  const char *pos = src;
  std::vector<uint32_t> code_points;
  while (*pos != 0) {
    uint8_t first_byte = static_cast<uint8_t>(*pos);
    uint8_t highbits = first_byte >> 4;
    int len = lookup[highbits];
    uint8_t mask = (1 << (8 - len)) - 1;
    uint32_t value = first_byte & mask;
    const char *end = pos + len;  // may overrun!
    ++pos;
    for (; pos < end && *pos != 0; ++pos) {
      value = (value << 6) + (static_cast<uint8_t>(*pos) & 0x3F);
    }
    code_points.push_back(value);
  }
  code_points.push_back(0);
  return code_points;
}

// returns true iff pos points to the end of one of the definitions of a rule
static bool llama_grammar_is_end_of_sequence(const llama_grammar_element *pos) {
  switch (pos->type) {
    case LLAMA_GRETYPE_END:
      return true;
    case LLAMA_GRETYPE_ALT:
      return true;
    default:
      return false;
  }
}

// returns true iff chr satisfies the char range at pos (regular or inverse
// range) asserts that pos is pointing to a char range element
static std::pair<bool, const llama_grammar_element *> llama_grammar_match_char(
    const llama_grammar_element *pos, const uint32_t chr) {
  bool found = false;
  bool is_positive_char = pos->type == LLAMA_GRETYPE_CHAR;
  LLAMA_ASSERT(is_positive_char || pos->type == LLAMA_GRETYPE_CHAR_NOT);

  do {
    if (pos[1].type == LLAMA_GRETYPE_CHAR_RNG_UPPER) {
      // inclusive range, e.g. [a-z]
      found = found || (pos->value <= chr && chr <= pos[1].value);
      pos += 2;
    } else {
      // exact char match, e.g. [a] or "a"
      found = found || pos->value == chr;
      pos += 1;
    }
  } while (pos->type == LLAMA_GRETYPE_CHAR_ALT);

  return std::make_pair(found == is_positive_char, pos);
}

// transforms a grammar pushdown stack into N possible stacks, all ending
// at a character range (terminal element)
static void llama_grammar_advance_stack(
    const std::vector<std::vector<llama_grammar_element>> &rules,
    const std::vector<const llama_grammar_element *> &stack,
    std::vector<std::vector<const llama_grammar_element *>> &new_stacks) {
  if (stack.empty()) {
    new_stacks.push_back(stack);
    return;
  }

  const llama_grammar_element *pos = stack.back();

  switch (pos->type) {
    case LLAMA_GRETYPE_RULE_REF: {
      const size_t rule_id = static_cast<size_t>(pos->value);
      const llama_grammar_element *subpos = rules[rule_id].data();
      do {
        // init new stack without the top (pos)
        std::vector<const llama_grammar_element *> new_stack(stack.begin(),
                                                             stack.end() - 1);
        if (!llama_grammar_is_end_of_sequence(pos + 1)) {
          // if this rule ref is followed by another element, add that to stack
          new_stack.push_back(pos + 1);
        }
        if (!llama_grammar_is_end_of_sequence(subpos)) {
          // if alternate is nonempty, add to stack
          new_stack.push_back(subpos);
        }
        llama_grammar_advance_stack(rules, new_stack, new_stacks);
        while (!llama_grammar_is_end_of_sequence(subpos)) {
          // scan to end of alternate def
          subpos++;
        }
        if (subpos->type == LLAMA_GRETYPE_ALT) {
          // there's another alternate def of this rule to process
          subpos++;
        } else {
          break;
        }
      } while (true);
      break;
    }
    case LLAMA_GRETYPE_CHAR:
    case LLAMA_GRETYPE_CHAR_NOT:
      new_stacks.push_back(stack);
      break;
    default:
      // end of alternate (LLAMA_GRETYPE_END, LLAMA_GRETYPE_ALT) or middle of
      // char range (LLAMA_GRETYPE_CHAR_ALT, LLAMA_GRETYPE_CHAR_RNG_UPPER);
      // stack should never be left on those
      LLAMA_ASSERT(false);
  }
}

// takes a set of possible pushdown stacks on a grammar, which are required to
// be positioned at a character range (see `llama_grammar_advance_stack`), and
// produces the N possible stacks if the given char is accepted at those
// positions
static std::vector<std::vector<const llama_grammar_element *>>
llama_grammar_accept(
    const std::vector<std::vector<llama_grammar_element>> &rules,
    const std::vector<std::vector<const llama_grammar_element *>> &stacks,
    const uint32_t chr) {
  std::vector<std::vector<const llama_grammar_element *>> new_stacks;

  for (const auto &stack : stacks) {
    if (stack.empty()) {
      continue;
    }

    auto match = llama_grammar_match_char(stack.back(), chr);
    if (match.first) {
      const llama_grammar_element *pos = match.second;

      // update top of stack to next element, if any
      std::vector<const llama_grammar_element *> new_stack(stack.begin(),
                                                           stack.end() - 1);
      if (!llama_grammar_is_end_of_sequence(pos)) {
        new_stack.push_back(pos);
      }
      llama_grammar_advance_stack(rules, new_stack, new_stacks);
    }
  }

  return new_stacks;
}

static std::vector<llama_grammar_candidate> llama_grammar_reject_candidates(
    const std::vector<std::vector<llama_grammar_element>> &rules,
    const std::vector<std::vector<const llama_grammar_element *>> &stacks,
    const std::vector<llama_grammar_candidate> &candidates);

static std::vector<llama_grammar_candidate>
llama_grammar_reject_candidates_for_stack(
    const std::vector<std::vector<llama_grammar_element>> &rules,
    const std::vector<const llama_grammar_element *> &stack,
    const std::vector<llama_grammar_candidate> &candidates) {
  std::vector<llama_grammar_candidate> rejects;

  if (stack.empty()) {
    // accept nothing; EOS is handled elsewhere
    rejects.insert(rejects.end(), candidates.begin(), candidates.end());
    return rejects;
  }

  const llama_grammar_element *stack_pos = stack.back();

  std::vector<llama_grammar_candidate> next_candidates;
  for (auto tok : candidates) {
    if (llama_grammar_match_char(stack_pos, tok.code_points[0]).first) {
      if (tok.code_points[1] != 0) {
        next_candidates.push_back({tok.index, tok.code_points + 1});
      }
    } else {
      rejects.push_back(tok);
    }
  }

  auto stack_pos_after = llama_grammar_match_char(stack_pos, 0).second;

  // update top of stack to next element, if any
  std::vector<const llama_grammar_element *> stack_after(stack.begin(),
                                                         stack.end() - 1);
  if (!llama_grammar_is_end_of_sequence(stack_pos_after)) {
    stack_after.push_back(stack_pos_after);
  }
  std::vector<std::vector<const llama_grammar_element *>> next_stacks;
  llama_grammar_advance_stack(rules, stack_after, next_stacks);

  auto next_rejects =
      llama_grammar_reject_candidates(rules, next_stacks, next_candidates);
  for (auto tok : next_rejects) {
    rejects.push_back({tok.index, tok.code_points - 1});
  }

  return rejects;
}

static std::vector<llama_grammar_candidate> llama_grammar_reject_candidates(
    const std::vector<std::vector<llama_grammar_element>> &rules,
    const std::vector<std::vector<const llama_grammar_element *>> &stacks,
    const std::vector<llama_grammar_candidate> &candidates) {
  LLAMA_ASSERT(!stacks.empty());  // REVIEW

  if (candidates.empty()) {
    return std::vector<llama_grammar_candidate>();
  }

  auto rejects = llama_grammar_reject_candidates_for_stack(
      rules, stacks.front(), candidates);

  for (size_t i = 1, size = stacks.size(); i < size; ++i) {
    rejects =
        llama_grammar_reject_candidates_for_stack(rules, stacks[i], rejects);
  }
  return rejects;
}

//
// grammar - external
//

struct llama_grammar *llama_grammar_init(const llama_grammar_element **rules,
                                         size_t n_rules,
                                         size_t start_rule_index) {
  const llama_grammar_element *pos;

  // copy rule definitions into vectors
  std::vector<std::vector<llama_grammar_element>> vec_rules(n_rules);
  for (size_t i = 0; i < n_rules; i++) {
    for (pos = rules[i]; pos->type != LLAMA_GRETYPE_END; pos++) {
      vec_rules[i].push_back(*pos);
    }
    vec_rules[i].push_back({LLAMA_GRETYPE_END, 0});
  }

  // loop over alternates of start rule to build initial stacks
  std::vector<std::vector<const llama_grammar_element *>> stacks;
  pos = rules[start_rule_index];
  do {
    std::vector<const llama_grammar_element *> stack;
    if (!llama_grammar_is_end_of_sequence(pos)) {
      // if alternate is nonempty, add to stack
      stack.push_back(pos);
    }
    llama_grammar_advance_stack(vec_rules, stack, stacks);
    while (!llama_grammar_is_end_of_sequence(pos)) {
      // scan to end of alternate def
      pos++;
    }
    if (pos->type == LLAMA_GRETYPE_ALT) {
      // there's another alternate def of this rule to process
      pos++;
    } else {
      break;
    }
  } while (true);

  return new llama_grammar{std::move(vec_rules), std::move(stacks)};
}

void llama_grammar_free(struct llama_grammar *grammar) { delete grammar; }

//
// sampling
//

void llama_sample_softmax(struct llama_context *ctx,
                          llama_token_data_array *candidates) {
  assert(candidates->size > 0);

  const int64_t t_start_sample_us = ggml_time_us();

  // Sort the logits in descending order
  if (!candidates->sorted) {
    std::sort(candidates->data, candidates->data + candidates->size,
              [](const llama_token_data &a, const llama_token_data &b) {
                return a.logit > b.logit;
              });
    candidates->sorted = true;
  }

  float max_l = candidates->data[0].logit;
  float cum_sum = 0.0f;
  for (size_t i = 0; i < candidates->size; ++i) {
    float p = expf(candidates->data[i].logit - max_l);
    candidates->data[i].p = p;
    cum_sum += p;
  }
  for (size_t i = 0; i < candidates->size; ++i) {
    candidates->data[i].p /= cum_sum;
  }

  if (ctx) {
    ctx->t_sample_us += ggml_time_us() - t_start_sample_us;
  }
}

void llama_sample_top_k(struct llama_context *ctx,
                        llama_token_data_array *candidates, int k,
                        size_t min_keep) {
  const int64_t t_start_sample_us = ggml_time_us();

  k = std::max(k, (int)min_keep);
  k = std::min(k, (int)candidates->size);

  // Sort scores in descending order
  if (!candidates->sorted) {
    auto comp = [](const llama_token_data &a, const llama_token_data &b) {
      return a.logit > b.logit;
    };
    if (k == (int)candidates->size) {
      std::sort(candidates->data, candidates->data + candidates->size, comp);
    } else {
      std::partial_sort(candidates->data, candidates->data + k,
                        candidates->data + candidates->size, comp);
    }
    candidates->sorted = true;
  }
  candidates->size = k;

  if (ctx) {
    ctx->t_sample_us += ggml_time_us() - t_start_sample_us;
  }
}

void llama_sample_top_p(struct llama_context *ctx,
                        llama_token_data_array *candidates, float p,
                        size_t min_keep) {
  if (p >= 1.0f) {
    return;
  }

  llama_sample_softmax(ctx, candidates);

  const int64_t t_start_sample_us = ggml_time_us();

  // Compute the cumulative probabilities
  float cum_sum = 0.0f;
  size_t last_idx = candidates->size;

  for (size_t i = 0; i < candidates->size; ++i) {
    cum_sum += candidates->data[i].p;

    // Check if the running sum is at least p or if we have kept at least
    // min_keep tokens we set the last index to i+1 to indicate that the current
    // iterate should be included in the set
    if (cum_sum >= p && i + 1 >= min_keep) {
      last_idx = i + 1;
      break;
    }
  }

  // Resize the output vector to keep only the top-p tokens
  candidates->size = last_idx;

  if (ctx) {
    ctx->t_sample_us += ggml_time_us() - t_start_sample_us;
  }
}

void llama_sample_tail_free(struct llama_context *ctx,
                            llama_token_data_array *candidates, float z,
                            size_t min_keep) {
  if (z >= 1.0f || candidates->size <= 2) {
    return;
  }

  llama_sample_softmax(nullptr, candidates);
  const int64_t t_start_sample_us = ggml_time_us();

  // Compute the first and second derivatives
  std::vector<float> first_derivatives(candidates->size - 1);
  std::vector<float> second_derivatives(candidates->size - 2);

  for (size_t i = 0; i < first_derivatives.size(); ++i) {
    first_derivatives[i] = candidates->data[i].p - candidates->data[i + 1].p;
  }
  for (size_t i = 0; i < second_derivatives.size(); ++i) {
    second_derivatives[i] = first_derivatives[i] - first_derivatives[i + 1];
  }

  // Calculate absolute value of second derivatives
  for (size_t i = 0; i < second_derivatives.size(); ++i) {
    second_derivatives[i] = abs(second_derivatives[i]);
  }

  // Normalize the second derivatives
  {
    const float second_derivatives_sum = std::accumulate(
        second_derivatives.begin(), second_derivatives.end(), 0.0f);

    if (second_derivatives_sum > 1e-6f) {
      for (float &value : second_derivatives) {
        value /= second_derivatives_sum;
      }
    } else {
      for (float &value : second_derivatives) {
        value = 1.0f / second_derivatives.size();
      }
    }
  }

  float cum_sum = 0.0f;
  size_t last_idx = candidates->size;
  for (size_t i = 0; i < second_derivatives.size(); ++i) {
    cum_sum += second_derivatives[i];

    // Check if the running sum is greater than z or if we have kept at least
    // min_keep tokens
    if (cum_sum > z && i >= min_keep) {
      last_idx = i;
      break;
    }
  }

  // Resize the output vector to keep only the tokens above the tail location
  candidates->size = last_idx;

  if (ctx) {
    ctx->t_sample_us += ggml_time_us() - t_start_sample_us;
  }
}

void llama_sample_typical(struct llama_context *ctx,
                          llama_token_data_array *candidates, float p,
                          size_t min_keep) {
  // Reference implementation:
  // https://github.com/huggingface/transformers/compare/main...cimeister:typical-sampling:typical-pr
  if (p >= 1.0f) {
    return;
  }

  // Compute the softmax of logits and calculate entropy
  llama_sample_softmax(nullptr, candidates);

  const int64_t t_start_sample_us = ggml_time_us();

  float entropy = 0.0f;
  for (size_t i = 0; i < candidates->size; ++i) {
    entropy += -candidates->data[i].p * logf(candidates->data[i].p);
  }

  // Compute the absolute difference between negative log probability and
  // entropy for each candidate
  std::vector<float> shifted_scores;
  for (size_t i = 0; i < candidates->size; ++i) {
    float shifted_score = fabsf(-logf(candidates->data[i].p) - entropy);
    shifted_scores.push_back(shifted_score);
  }

  // Sort tokens based on the shifted_scores and their corresponding indices
  std::vector<size_t> indices(candidates->size);
  std::iota(indices.begin(), indices.end(), 0);

  std::sort(indices.begin(), indices.end(), [&](size_t a, size_t b) {
    return shifted_scores[a] < shifted_scores[b];
  });

  // Compute the cumulative probabilities
  float cum_sum = 0.0f;
  size_t last_idx = indices.size();

  for (size_t i = 0; i < indices.size(); ++i) {
    size_t idx = indices[i];
    cum_sum += candidates->data[idx].p;

    // Check if the running sum is greater than typical or if we have kept at
    // least min_keep tokens
    if (cum_sum > p && i >= min_keep - 1) {
      last_idx = i + 1;
      break;
    }
  }

  // Resize the output vector to keep only the locally typical tokens
  std::vector<llama_token_data> new_candidates;
  for (size_t i = 0; i < last_idx; ++i) {
    size_t idx = indices[i];
    new_candidates.push_back(candidates->data[idx]);
  }

  // Replace the data in candidates with the new_candidates data
  std::copy(new_candidates.begin(), new_candidates.end(), candidates->data);
  candidates->size = new_candidates.size();

  if (ctx) {
    ctx->t_sample_us += ggml_time_us() - t_start_sample_us;
  }
}

void llama_sample_temperature(struct llama_context *ctx,
                              llama_token_data_array *candidates_p,
                              float temp) {
  const int64_t t_start_sample_us = ggml_time_us();

  for (size_t i = 0; i < candidates_p->size; ++i) {
    candidates_p->data[i].logit /= temp;
  }

  if (ctx) {
    ctx->t_sample_us += ggml_time_us() - t_start_sample_us;
  }
}

void llama_sample_repetition_penalty(struct llama_context *ctx,
                                     llama_token_data_array *candidates,
                                     const llama_token *last_tokens,
                                     size_t last_tokens_size, float penalty) {
  if (last_tokens_size == 0 || penalty == 1.0f) {
    return;
  }

  const int64_t t_start_sample_us = ggml_time_us();

  for (size_t i = 0; i < candidates->size; ++i) {
    const auto *token_iter = std::find(
        last_tokens, last_tokens + last_tokens_size, candidates->data[i].id);
    if (token_iter == last_tokens + last_tokens_size) {
      continue;
    }

    // The academic publication that described this technique actually just only
    // divided, but that would cause tokens with negative logits to become more
    // likely, which is obviously wrong. This is common fix for this problem,
    // which is to multiply by the penalty instead of dividing.
    if (candidates->data[i].logit <= 0) {
      candidates->data[i].logit *= penalty;
    } else {
      candidates->data[i].logit /= penalty;
    }
  }

  candidates->sorted = false;

  if (ctx) {
    ctx->t_sample_us += ggml_time_us() - t_start_sample_us;
  }
}

void llama_sample_frequency_and_presence_penalties(
    struct llama_context *ctx, llama_token_data_array *candidates,
    const llama_token *last_tokens_p, size_t last_tokens_size,
    float alpha_frequency, float alpha_presence) {
  if (last_tokens_size == 0 ||
      (alpha_frequency == 0.0f && alpha_presence == 0.0f)) {
    return;
  }

  const int64_t t_start_sample_us = ggml_time_us();

  // Create a frequency map to count occurrences of each token in last_tokens
  std::unordered_map<llama_token, int> token_count;
  for (size_t i = 0; i < last_tokens_size; ++i) {
    token_count[last_tokens_p[i]]++;
  }

  // Apply frequency and presence penalties to the candidates
  for (size_t i = 0; i < candidates->size; ++i) {
    auto token_iter = token_count.find(candidates->data[i].id);
    if (token_iter == token_count.end()) {
      continue;
    }

    int count = token_iter->second;
    candidates->data[i].logit -=
        float(count) * alpha_frequency + float(count > 0) * alpha_presence;
  }

  candidates->sorted = false;

  if (ctx) {
    ctx->t_sample_us += ggml_time_us() - t_start_sample_us;
  }
}

void llama_sample_grammar(struct llama_context *ctx,
                          llama_token_data_array *candidates,
                          const struct llama_grammar *grammar) {
  assert(ctx);
  const int64_t t_start_sample_us = ggml_time_us();

  bool allow_eos = false;
  for (const auto &stack : grammar->stacks) {
    if (stack.empty()) {
      allow_eos = true;
      break;
    }
  }

  const llama_token eos = llama_token_eos();

  std::vector<std::vector<uint32_t>> candidates_decoded;
  std::vector<llama_grammar_candidate> candidates_grammar;

  for (size_t i = 0; i < candidates->size; ++i) {
    const llama_token id = candidates->data[i].id;
    const char *str = llama_token_to_str(ctx, id);
    if (id == eos) {
      if (!allow_eos) {
        candidates->data[i].logit = -INFINITY;
      }
    } else if (*str == 0) {
      candidates->data[i].logit = -INFINITY;
    } else {
      candidates_decoded.push_back(decode_utf8(str));
      candidates_grammar.push_back({i, candidates_decoded.back().data()});
    }
  }

  const auto rejects = llama_grammar_reject_candidates(
      grammar->rules, grammar->stacks, candidates_grammar);
  for (auto &reject : rejects) {
    candidates->data[reject.index].logit = -INFINITY;
  }

  ctx->t_sample_us += ggml_time_us() - t_start_sample_us;
}

static void llama_log_softmax(float *array, size_t size) {
  float max_l = *std::max_element(array, array + size);
  float sum = 0.f;
  for (size_t i = 0; i < size; ++i) {
    float p = expf(array[i] - max_l);
    sum += p;
    array[i] = p;
  }

  for (size_t i = 0; i < size; ++i) {
    array[i] = logf(array[i] / sum);
  }
}

void llama_sample_classifier_free_guidance(struct llama_context *ctx,
                                           llama_token_data_array *candidates,
                                           struct llama_context *guidance_ctx,
                                           float scale) {
  int64_t t_start_sample_us = ggml_time_us();

  assert(ctx);
  auto n_vocab = llama_n_vocab(ctx);
  assert(n_vocab == (int)candidates->size);
  assert(!candidates->sorted);

  std::vector<float> logits_base;
  logits_base.reserve(candidates->size);
  for (size_t i = 0; i < candidates->size; ++i) {
    logits_base.push_back(candidates->data[i].logit);
  }
  llama_log_softmax(logits_base.data(), candidates->size);

  float *logits_guidance = llama_get_logits(guidance_ctx);
  llama_log_softmax(logits_guidance, n_vocab);

  for (int i = 0; i < n_vocab; ++i) {
    float logit_guidance = logits_guidance[i];
    float logit_base = logits_base[i];
    candidates->data[i].logit =
        scale * (logit_base - logit_guidance) + logit_guidance;
  }

  if (ctx) {
    ctx->t_sample_us += ggml_time_us() - t_start_sample_us;
  }
}

llama_token llama_sample_token_mirostat(struct llama_context *ctx,
                                        llama_token_data_array *candidates,
                                        float tau, float eta, int m,
                                        float *mu) {
  assert(ctx);
  auto N = float(llama_n_vocab(ctx));
  int64_t t_start_sample_us;
  t_start_sample_us = ggml_time_us();

  llama_sample_softmax(nullptr, candidates);

  // Estimate s_hat using the most probable m tokens
  float s_hat = 0.0;
  float sum_ti_bi = 0.0;
  float sum_ti_sq = 0.0;
  for (size_t i = 0; i < size_t(m - 1) && i < candidates->size - 1; ++i) {
    float t_i = logf(float(i + 2) / float(i + 1));
    float b_i = logf(candidates->data[i].p / candidates->data[i + 1].p);
    sum_ti_bi += t_i * b_i;
    sum_ti_sq += t_i * t_i;
  }
  s_hat = sum_ti_bi / sum_ti_sq;

  // Compute k from the estimated s_hat and target surprise value
  float epsilon_hat = s_hat - 1;
  float k = powf((epsilon_hat * powf(2, *mu)) / (1 - powf(N, -epsilon_hat)),
                 1 / s_hat);

  // Sample the next word X using top-k sampling
  llama_sample_top_k(nullptr, candidates, int(k), 1);
  if (ctx) {
    ctx->t_sample_us += ggml_time_us() - t_start_sample_us;
  }
  llama_token X = llama_sample_token(ctx, candidates);
  t_start_sample_us = ggml_time_us();

  // Compute error as the difference between observed surprise and target
  // surprise value
  size_t X_idx = std::distance(
      candidates->data,
      std::find_if(candidates->data, candidates->data + candidates->size,
                   [&](const llama_token_data &candidate) {
                     return candidate.id == X;
                   }));
  float observed_surprise = -log2f(candidates->data[X_idx].p);
  float e = observed_surprise - tau;

  // Update mu using the learning rate and error
  *mu = *mu - eta * e;

  if (ctx) {
    ctx->t_sample_us += ggml_time_us() - t_start_sample_us;
  }
  return X;
}

llama_token llama_sample_token_mirostat_v2(struct llama_context *ctx,
                                           llama_token_data_array *candidates,
                                           float tau, float eta, float *mu) {
  int64_t t_start_sample_us;
  t_start_sample_us = ggml_time_us();

  llama_sample_softmax(ctx, candidates);

  // Truncate the words with surprise values greater than mu
  candidates->size = std::distance(
      candidates->data,
      std::find_if(candidates->data, candidates->data + candidates->size,
                   [&](const llama_token_data &candidate) {
                     return -log2f(candidate.p) > *mu;
                   }));

  if (candidates->size == 0) {
    candidates->size = 1;
  }

  if (ctx) {
    ctx->t_sample_us += ggml_time_us() - t_start_sample_us;
  }

  // Normalize the probabilities of the remaining words
  llama_sample_softmax(ctx, candidates);

  // Sample the next word X from the remaining words
  llama_token X = llama_sample_token(ctx, candidates);
  t_start_sample_us = ggml_time_us();

  // Compute error as the difference between observed surprise and target
  // surprise value
  size_t X_idx = std::distance(
      candidates->data,
      std::find_if(candidates->data, candidates->data + candidates->size,
                   [&](const llama_token_data &candidate) {
                     return candidate.id == X;
                   }));
  float observed_surprise = -log2f(candidates->data[X_idx].p);
  float e = observed_surprise - tau;

  // Update mu using the learning rate and error
  *mu = *mu - eta * e;

  if (ctx) {
    ctx->t_sample_us += ggml_time_us() - t_start_sample_us;
  }
  return X;
}

llama_token llama_sample_token_greedy(struct llama_context *ctx,
                                      llama_token_data_array *candidates) {
  const int64_t t_start_sample_us = ggml_time_us();

  // Find max element
  auto *max_iter = std::max_element(
      candidates->data, candidates->data + candidates->size,
      [](const llama_token_data &a, const llama_token_data &b) {
        return a.logit < b.logit;
      });

  llama_token result = max_iter->id;
  if (ctx) {
    ctx->t_sample_us += ggml_time_us() - t_start_sample_us;
    ctx->n_sample++;
  }
  return result;
}

llama_token llama_sample_token(struct llama_context *ctx,
                               llama_token_data_array *candidates) {
  assert(ctx);
  const int64_t t_start_sample_us = ggml_time_us();
  llama_sample_softmax(nullptr, candidates);

  std::vector<float> probs;
  probs.reserve(candidates->size);
  for (size_t i = 0; i < candidates->size; ++i) {
    probs.push_back(candidates->data[i].p);
  }

  std::discrete_distribution<> dist(probs.begin(), probs.end());
  auto &rng = ctx->rng;
  int idx = dist(rng);

  llama_token result = candidates->data[idx].id;

  ctx->t_sample_us += ggml_time_us() - t_start_sample_us;
  ctx->n_sample++;
  return result;
}

//
// interface implementation
//

struct llama_model *llama_load_model_from_file(
    const char *path_model, struct llama_context_params params) {
  ggml_time_init();

  llama_model *model = new llama_model;

  ggml_type memory_type = params.f16_kv ? GGML_TYPE_F16 : GGML_TYPE_F32;

  if (!llama_model_load(
          path_model, *model, model->vocab, params.n_ctx, params.n_batch,
          params.n_gqa, params.rms_norm_eps, params.n_gpu_layers,
          params.main_gpu, params.tensor_split, params.mul_mat_q,
          params.rope_freq_base, params.rope_freq_scale, params.low_vram,
          memory_type, params.use_mmap, params.use_mlock, params.vocab_only,
          params.progress_callback, params.progress_callback_user_data)) {
    delete model;
    fprintf(stderr, "%s: failed to load model\n", __func__);
    return nullptr;
  }

  return model;
}

void llama_free_model(struct llama_model *model) { delete model; }

struct llama_context *llama_new_context_with_model(
    struct llama_model *model, struct llama_context_params params) {
  if (!model) {
    return nullptr;
  }

  llama_context *ctx = new llama_context(*model);

  if (params.seed == LLAMA_DEFAULT_SEED) {
    params.seed = time(NULL);
  }

  unsigned cur_percentage = 0;
  if (params.progress_callback == NULL) {
    params.progress_callback_user_data = &cur_percentage;
    params.progress_callback = [](float progress, void *ctx) {
      unsigned *cur_percentage_p = (unsigned *)ctx;
      unsigned percentage = (unsigned)(100 * progress);
      while (percentage > *cur_percentage_p) {
        *cur_percentage_p = percentage;
      }
    };
  }

  ctx->rng = std::mt19937(params.seed);
  ctx->logits_all = params.logits_all;

  ggml_type memory_type = params.f16_kv ? GGML_TYPE_F16 : GGML_TYPE_F32;

  // reserve memory for context buffers
  if (!params.vocab_only) {
    if (!kv_cache_init(ctx->model.hparams, ctx->kv_self, memory_type,
                       ctx->model.hparams.n_ctx, params.n_gpu_layers)) {
      fprintf(stderr, "%s: kv_cache_init() failed for self-attention cache\n",
              __func__);
      llama_free(ctx);
      return nullptr;
    }

    const auto &hparams = ctx->model.hparams;

    // resized during inference
    if (params.logits_all) {
      ctx->logits.reserve(hparams.n_ctx * hparams.n_vocab);
    } else {
      ctx->logits.reserve(hparams.n_vocab);
    }

    if (params.embedding) {
      ctx->embedding.resize(hparams.n_embd);
    }

#ifdef LLAMA_USE_ALLOCATOR
    {
      static const size_t tensor_alignment = 32;
      // the compute buffer is used to store the tensor and graph structs, while
      // the allocator buffer is used for the tensor data
      ctx->buf_compute.resize(ggml_tensor_overhead() * GGML_MAX_NODES +
                              ggml_graph_overhead());

      // create measure allocator
      ctx->alloc = ggml_allocr_new_measure(tensor_alignment);

      // build worst-case graph
      int n_tokens = std::min((int)hparams.n_ctx, params.n_batch);
      int n_past = hparams.n_ctx - n_tokens;
      llama_token token =
          llama_token_bos();  // not actually used by llama_build_graph, but
                              // required to choose between token and embedding
                              // inputs graph
      ggml_cgraph *gf = llama_build_graph(*ctx, &token, NULL, n_tokens, n_past);

      // measure memory requirements for the graph
      size_t alloc_size =
          ggml_allocr_alloc_graph(ctx->alloc, gf) + tensor_alignment;

      // debug - for comparison with scratch buffer
      // size_t prev_req =
      //    MEM_REQ_SCRATCH0(hparams.n_ctx).at(ctx->model.type) +
      //    MEM_REQ_SCRATCH1().at(ctx->model.type) +
      //    MEM_REQ_EVAL().at(ctx->model.type);
      // fprintf(stderr, "%s: (debug) equivalent with scratch buffer = %7.2f
      // MB\n", __func__, prev_req / 1024.0 / 1024.0);

      // recreate allocator with exact memory requirements
      ggml_allocr_free(ctx->alloc);

      ctx->buf_alloc.resize(alloc_size);
      ctx->alloc = ggml_allocr_new(ctx->buf_alloc.addr, ctx->buf_alloc.size,
                                   tensor_alignment);
    }
#else
    ctx->buf_compute.resize(MEM_REQ_EVAL().at(ctx->model.type) +
                            ggml_graph_overhead());
#endif

#ifdef LLAMA_USE_SCRATCH
    ctx->buf_scratch[0].resize(
        MEM_REQ_SCRATCH0(hparams.n_ctx).at(ctx->model.type));
    ctx->buf_scratch[1].resize(MEM_REQ_SCRATCH1().at(ctx->model.type));
#endif
  }

#ifdef GGML_USE_METAL
  if (params.n_gpu_layers > 0) {
    // this allocates all Metal resources and memory buffers
    ctx->ctx_metal = ggml_metal_init(1);

    void *data_ptr = NULL;
    size_t data_size = 0;

    if (params.use_mmap) {
      data_ptr = ctx->model.mapping->addr;
      data_size = ctx->model.mapping->size;
    } else {
      data_ptr = ggml_get_mem_buffer(ctx->model.ctx);
      data_size = ggml_get_mem_size(ctx->model.ctx);
    }

    const size_t max_size = ggml_get_max_tensor_size(ctx->model.ctx);

#define LLAMA_METAL_CHECK_BUF(result)                        \
  if (!(result)) {                                           \
    fprintf(stderr, "%s: failed to add buffer\n", __func__); \
    llama_free(ctx);                                         \
    return NULL;                                             \
  }

    LLAMA_METAL_CHECK_BUF(ggml_metal_add_buffer(ctx->ctx_metal, "data",
                                                data_ptr, data_size, max_size));

    LLAMA_METAL_CHECK_BUF(ggml_metal_add_buffer(ctx->ctx_metal, "eval",
                                                ctx->buf_compute.addr,
                                                ctx->buf_compute.size, 0));
    LLAMA_METAL_CHECK_BUF(ggml_metal_add_buffer(
        ctx->ctx_metal, "kv", ctx->kv_self.buf.addr, ctx->kv_self.buf.size, 0));

    LLAMA_METAL_CHECK_BUF(ggml_metal_add_buffer(ctx->ctx_metal, "scr0",
                                                ctx->buf_scratch[0].addr,
                                                ctx->buf_scratch[0].size, 0));
    LLAMA_METAL_CHECK_BUF(ggml_metal_add_buffer(ctx->ctx_metal, "scr1",
                                                ctx->buf_scratch[1].addr,
                                                ctx->buf_scratch[1].size, 0));
#undef LLAMA_METAL_CHECK_BUF
  }
#endif

#ifdef GGML_USE_MPI
  ctx->ctx_mpi = ggml_mpi_init();

  if (ggml_mpi_rank(ctx->ctx_mpi) > 0) {
    // Enter a blocking eval loop with dummy input, letting rank=0 drive the
    // process
    const std::vector<llama_token> tmp(ctx->model.hparams.n_ctx,
                                       llama_token_bos());
    while (!llama_eval(ctx, tmp.data(), tmp.size(), 0, 0)) {
    };
    llama_backend_free();
    exit(1);
  }
#endif

  return ctx;
}

struct llama_context *llama_init_from_file(const char *path_model,
                                           struct llama_context_params params) {
  struct llama_model *model = llama_load_model_from_file(path_model, params);
  if (!model) {
    return nullptr;
  }
  struct llama_context *ctx = llama_new_context_with_model(model, params);
  ctx->model_owner = true;
  return ctx;
}

void llama_free(struct llama_context *ctx) { delete ctx; }

int llama_get_kv_cache_token_count(const struct llama_context *ctx) {
  return ctx->kv_self.n;
}

void llama_set_rng_seed(struct llama_context *ctx, uint32_t seed) {
  if (seed == LLAMA_DEFAULT_SEED) {
    seed = time(NULL);
  }
  ctx->rng.seed(seed);
}

int llama_eval(struct llama_context *ctx, const llama_token *tokens,
               int n_tokens, int n_past, int n_threads) {
  if (!llama_eval_internal(*ctx, tokens, nullptr, n_tokens, n_past, n_threads,
                           nullptr)) {
    fprintf(stderr, "%s: failed to eval\n", __func__);
    return 1;
  }

  // get a more accurate load time, upon first eval
  // TODO: fix this
  if (!ctx->has_evaluated_once) {
    ctx->t_load_us = ggml_time_us() - ctx->t_start_us;
    ctx->has_evaluated_once = true;
  }

  return 0;
}

int llama_eval_embd(struct llama_context *ctx, const float *embd, int n_tokens,
                    int n_past, int n_threads) {
  if (!llama_eval_internal(*ctx, nullptr, embd, n_tokens, n_past, n_threads,
                           nullptr)) {
    fprintf(stderr, "%s: failed to eval\n", __func__);
    return 1;
  }

  // get a more accurate load time, upon first eval
  // TODO: fix this
  if (!ctx->has_evaluated_once) {
    ctx->t_load_us = ggml_time_us() - ctx->t_start_us;
    ctx->has_evaluated_once = true;
  }

  return 0;
}

int llama_eval_export(struct llama_context *ctx, const char *fname) {
  const int n_batch = 1;
  const int n_ctx = 512 - n_batch;

  const std::vector<llama_token> tmp(n_batch, llama_token_bos());

  if (!llama_eval_internal(*ctx, tmp.data(), nullptr, tmp.size(), n_ctx, 1,
                           fname)) {
    fprintf(stderr, "%s: failed to eval\n", __func__);
    return 1;
  }

  return 0;
}

int llama_tokenize_with_model(const struct llama_model *model, const char *text,
                              llama_token *tokens, int n_max_tokens,
                              bool add_bos) {
  auto res = llama_tokenize(model->vocab, text, add_bos);

  if (n_max_tokens < (int)res.size()) {
    fprintf(stderr, "%s: too many tokens\n", __func__);
    return -((int)res.size());
  }

  for (size_t i = 0; i < res.size(); i++) {
    tokens[i] = res[i];
  }

  return res.size();
}

int llama_tokenize(struct llama_context *ctx, const char *text,
                   llama_token *tokens, int n_max_tokens, bool add_bos) {
  return llama_tokenize_with_model(&ctx->model, text, tokens, n_max_tokens,
                                   add_bos);
}

int llama_n_vocab_from_model(const struct llama_model *model) {
  return model->vocab.id_to_token.size();
}

int llama_n_ctx_from_model(const struct llama_model *model) {
  return model->hparams.n_ctx;
}

int llama_n_embd_from_model(const struct llama_model *model) {
  return model->hparams.n_embd;
}

int llama_n_vocab(const struct llama_context *ctx) {
  return ctx->model.vocab.id_to_token.size();
}

int llama_n_ctx(const struct llama_context *ctx) {
  return ctx->model.hparams.n_ctx;
}

int llama_n_embd(const struct llama_context *ctx) {
  return ctx->model.hparams.n_embd;
}

int llama_get_vocab_from_model(const struct llama_model *model,
                               const char **strings, float *scores,
                               int capacity) {
  int n = std::min(capacity, (int)model->vocab.id_to_token.size());
  for (int i = 0; i < n; ++i) {
    strings[i] = model->vocab.id_to_token[i].tok.c_str();
    scores[i] = model->vocab.id_to_token[i].score;
  }
  return n;
}

int llama_get_vocab(const struct llama_context *ctx, const char **strings,
                    float *scores, int capacity) {
  return llama_get_vocab_from_model(&ctx->model, strings, scores, capacity);
}

float *llama_get_logits(struct llama_context *ctx) {
  return ctx->logits.data();
}

float *llama_get_embeddings(struct llama_context *ctx) {
  return ctx->embedding.data();
}

const char *llama_token_to_str_with_model(const struct llama_model *model,
                                          llama_token token) {
  if (token >= llama_n_vocab_from_model(model)) {
    return nullptr;
  }

  return model->vocab.id_to_token[token].tok.c_str();
}

const char *llama_token_to_str(const struct llama_context *ctx,
                               llama_token token) {
  return llama_token_to_str_with_model(&ctx->model, token);
}

llama_token llama_token_bos() { return 1; }

llama_token llama_token_eos() { return 2; }

llama_token llama_token_nl() { return 13; }

}  // namespace llama_ggml
