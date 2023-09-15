from terraformmetrics.import_metrics import general_metrics, tf_metrics

def extract_all(script: str):
    if script is None:
        raise TypeError('Expected a string')

    metrics = general_metrics
    metrics.update(tf_metrics)

    results = dict()

    # Execute metrics
    for name in metrics:
        results[name] = metrics[name](script).count()

    return results
