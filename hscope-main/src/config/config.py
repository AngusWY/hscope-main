import os

ROOT_DIR = os.path.realpath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
print(ROOT_DIR)
ENGINE_DIR = os.path.join(ROOT_DIR, "src/engine/src")
TAINT_DIR1 = os.path.join(ROOT_DIR, "/src")
TAINT_DIR = os.path.join(ENGINE_DIR, "engine/taintv2")
ANALYZER_DIR = os.path.join(ROOT_DIR, "src")

DEFAULT_WORKSPACE       = os.path.join(ROOT_DIR, "test/abc_workspace")
LANG_NAME               = "abc"
LANG_EXTENSION          = [".txt"]
LANG_SO_PATH            = os.path.join(ANALYZER_DIR, "frontend/abc_lang_linux.so")
OUT_DIR                 = "out"
EXTERN_SYSTEM_DIR       = os.path.join(ANALYZER_DIR, "externs")

LRU_CACHE_CAPACITY      = 10000
BUNDLE_CACHE_CAPACITY   = 10
