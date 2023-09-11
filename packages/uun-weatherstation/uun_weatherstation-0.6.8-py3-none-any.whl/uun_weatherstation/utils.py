def fahrenheit_to_celsius(fahrenheit):
  if fahrenheit is not None:
    return round((fahrenheit - 32)*5.0/9.0, 1)
  else:
    return None

def mph_to_kph(mph):
  if mph is not None:
    return mph * 1.60934
  else:
    return None

def inch_to_cm(inch):
  if inch is not None:
    return inch * 2.54
  else:
    return None

