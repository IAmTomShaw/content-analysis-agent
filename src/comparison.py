def compare_to_baseline(video_metrics, baseline_metrics, checkpoint="24hr"):
  results = {}
  for metric, value in video_metrics.items():
    if checkpoint in metric:
      base_value = baseline_metrics.get(metric, 0)
      if base_value > 0:
        delta = ((value - base_value) / base_value) * 100
      else:
        delta = None
      results[metric] = {"value": value, "baseline": base_value, "delta": round(delta, 1) if delta is not None else None}
  return results