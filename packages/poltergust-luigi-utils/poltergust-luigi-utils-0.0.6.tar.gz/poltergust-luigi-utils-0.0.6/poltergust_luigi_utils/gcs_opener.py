import luigi
import luigi.contrib.gcs
import luigi.format
import luigi.contrib.opener

class GCSOpener(luigi.contrib.opener.Opener):
    """Opens a target stored on Google GCS

    examples:
    * gs://bucket/foo/bar.txt

    """
    names = ['gs']
    allowed_kwargs = {
        'format': True,
        'client': True,
    }
    filter_kwargs = False

    @classmethod
    def get_target(cls, scheme, path, fragment, username,
                   password, hostname, port, query, **kwargs):
        import luigi.contrib.gcs
        query.update(kwargs)
        return luigi.contrib.gcs.GCSTarget('{scheme}://{hostname}{path}'.format(
            scheme=scheme, hostname=hostname, path=path), **query)
    
luigi.contrib.opener.opener.add(GCSOpener)
