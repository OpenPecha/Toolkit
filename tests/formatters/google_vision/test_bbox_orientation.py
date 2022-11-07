from openpecha.formatters.ocr import GoogleVisionFormatter

# 43 
# 12

test_0 =	[
    {
        "x": 816,
        "y": 388
    },
    {
        "x": 3635,
        "y": 388
    },
    {
        "x": 3635,
        "y": 672
    },
    {
        "x": 816,
        "y": 672
    }
]

expected_0 = [816,3635,388,672,0]

# 32 
# 41

test_90 = [
  {
    "x": 880,
    "y": 388
  },
  {
    "x": 880,
    "y": 411
  },
  {
    "x": 817,
    "y": 411
  },
  {
    "x": 817,
    "y": 388
  }
]

expected_90 = [817,880,388,411,90]

# in this attested example, the polygon is not a rectangle
test_90_2 = [
  {
    "x": 842,
    "y": 304
  },
  {
    "x": 843,
    "y": 377
  },
  {
    "x": 758,
    "y": 378
  },
  {
    "x": 757,
    "y": 305
  }
]

expected_90_2 = [757,843,304,378,90]

# not attested yet, guess is

# 21
# 34

test_180 = [
    {
        "x": 884,
        "y": 672
    },
    {
        "x": 832,
        "y": 672
    },
    {
        "x": 832,
        "y": 611
    },
    {
        "x": 884,
        "y": 611
    }
]

expected_180 = [832,884,611,672,180]

# not attested yet, guess is

# 14
# 23

test_270 = [
    {
        "x": 832,
        "y": 672
    },
    {
        "x": 832,
        "y": 611
    },
    {
        "x": 884,
        "y": 611
    },
    {
        "x": 884,
        "y": 672
    }
]

expected_270 = [832,884,611,672,270]

def test_bbox_info():
    assert(GoogleVisionFormatter.get_bboxinfo_from_vertices(test_0) == expected_0)
    assert(GoogleVisionFormatter.get_bboxinfo_from_vertices(test_90) == expected_90)
    assert(GoogleVisionFormatter.get_bboxinfo_from_vertices(test_90_2) == expected_90_2)
    assert(GoogleVisionFormatter.get_bboxinfo_from_vertices(test_180) == expected_180)
    assert(GoogleVisionFormatter.get_bboxinfo_from_vertices(test_270) == expected_270)

