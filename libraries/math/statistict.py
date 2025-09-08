def mean_ungroup(n):
  return sum(n) / len(n)

def mean_group(l, h, f):
  return sum([((l + (i * h)) * f[i]) for i in range(len(f))]) / sum(f)

def median_ungroup(n):
  n = sorted(n)
  length = len(n)
  if length % 2 == 0:
    median = (n[length//2 - 1] + n[length//2]) / 2
  else:
    median = n[length//2]
  return median

def median_group(l, h, f):
  cf = [f[0]]
  for i in range(1, len(f)):
    cf.append(cf[i-1] + f[i])
  n = sum(f)
  median_class_index = next(i for i, v in enumerate(cf) if v >= n / 2)
  median_class_lower_bound = l + (median_class_index * h)
  median_class_frequency = f[median_class_index]
  cumulative_frequency_before_median_class = cf[median_class_index - 1] if median_class_index > 0 else 0
  median = median_class_lower_bound + ((n / 2 - cumulative_frequency_before_median_class) / median_class_frequency) * h
  return median

def mode_ungroup(n):
  frequency = {}
  for value in n:
    frequency[value] = frequency.get(value, 0) + 1
  mode = max(frequency.items(), key=lambda x: x[1])[0]
  return mode

def mode_group(l, h, f):
  mode_class_index = f.index(max(f))
  mode = l + (mode_class_index * h)
  return mode

def standard_deviation(numbers):
  if len(numbers) < 2:
    return None
  mean = mean_ungroup(numbers)
  squared_diff_sum = sum((x - mean) ** 2 for x in numbers)
  variance = squared_diff_sum / (len(numbers) - 1)
  return (variance ** 0.5)