用 pillow 画目标检测的框，支持中文（自带字体）

用法见

[→ test.py](test.py)

```py
#!/usr/bin/env python

from imgbox import imgbox
from PIL import Image
from os.path import abspath, dirname, join

DIR = dirname(abspath(__file__))
img = join(DIR, 'test.webp')
img = Image.open(img)
imgbox(img, ('测试', (30, 30, 60, 60)))
img.save(join(DIR, 'box.webp'), quality=80)
```

