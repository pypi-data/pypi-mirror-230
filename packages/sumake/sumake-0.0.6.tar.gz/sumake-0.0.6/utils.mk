UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Linux)
# pass
else ifeq ($(UNAME_S),Darwin)
# pass
endif

.PHONY: wget_if_not_exist

define wget_if_not_exist
@if [ ! -f $(1) ]; then \
	mkdir -p $(dir $(1)); \
	wget -O $(1) $(2); \
else \
	echo "File already exists: $(1) "; \
fi
endef

#sumake_version:
#	@echo 2023.5.9

# $(call check_conda, my_env)
#define check_conda
#$(eval conda_env := $(1)) \
#if [ $(USE_CONDA) != false ]; then \
#$(eval CONDA_RUN := conda run -n $(conda_env) --no-capture-output); \
#fi
#endef
# 这一行放到里面就不起作用了，我也不知道为什么
export conda_run = conda run -n $(CONDA_ENV) --no-capture-output
ifeq ($(USE_CONDA),false)
	export conda_run=
endif
#if $(filter $(conda) $(USE_CONDA),false),, $(eval CONDA_RUN := conda run -n $(conda_env) --no-capture-output))
DEPLOY_USERNAME ?= $(USERNAME)
#DEPLOY_USERNAME ?= peng

DEPLOY_PORT ?= 22
DEPLOY_HOST ?= $(DEPLOY_USERNAME)@$(DEPLOY_ADDRESS)
define upload
	@rsync -av  \
		--rsh="ssh -o StrictHostKeyChecking=no -p $(DEPLOY_PORT)" \
		$(1) \
		${DEPLOY_HOST}:$(patsubst %,%, $(if $(2),$(2),~/$(patsubst %,%,$(1))))
endef

define command
	ssh -p $(DEPLOY_PORT) $(DEPLOY_HOST) $(1)
endef
