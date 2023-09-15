from .WriterNonCDC import WriterNonCDC
from .WriterCDC import WriterCDC


def constructor(env, struct, migrator_redshift_connector, update_by_cdc):
    if update_by_cdc is False:
        return WriterNonCDC(env, struct, migrator_redshift_connector)
    else:
        pass
        return WriterCDC(env, struct, migrator_redshift_connector)
