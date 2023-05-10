import vedro
import vedro_jj
import vedro_valera_validator as valera_validator


class Config(vedro.Config):
    class Plugins(vedro.Config.Plugins):
        class ValeraValidator(valera_validator.ValeraValidator):
            enabled = True

        class RemoteMock(vedro_jj.RemoteMock):
            enabled = True
