from localstack.runtime import hooks
@hooks.on_infra_start()
def register_pickle_patches_runtime():'Adds the pickling patches to the runtime (e.g., when using the CLI)';from.reducers import register as A;A()
@hooks.prepare_host()
def register_pickle_patches_host():'Adds the pickling patches to the host (e.g., when using the CLI)';from.reducers import register as A;A()