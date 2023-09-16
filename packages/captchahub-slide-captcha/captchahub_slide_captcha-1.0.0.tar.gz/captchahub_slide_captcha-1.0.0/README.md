# slide captcha

## 介绍
一个尝试使用opencv识别滑动验证码缺口的python库

## 免责声明

1. 本算法仅供学术和研究目的使用。作者和发布者明确禁止使用此算法进行任何非法活动或违反任何网站、服务或应用的服务条款或政策。
2. 使用此算法的任何人都应自行确保他们的行为是合法的，并遵循所有相关的法律和道德标准。
3. 作者和发布者对因使用此算法而造成的任何直接或间接损害或后果不承担任何责任。用户自行承担所有风险。
4. 本免责声明的解释权归作者和发布者所有。


## 安装
```shell
pip install captchahub-slide-captcha
```·
## 使用
```python
from slide_captcha import slide_match

with open('background.png', 'rb') as f:
    background = f.read()

with open('target.png', 'rb') as f:
    target = f.read()

result = slide_match(background, target)

print(result)
# {'target': [192, 111, 272, 191]}
```
target为缺口的左上角和右下角的坐标