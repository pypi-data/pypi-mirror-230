# Usage:

`pip install url-local`

```python
from url_local.url_circlez import UrlCirclez

UrlCirclez.endpoint_url(BrandName.CIRCLEZ.value, EnvironmentName.PLAY1.value,
                        ComponentName.GENDER_DETECTION.value, EntityName.GENDER_DETECTION.value, 1,
                        ActionName.ANALYZE_FACIAL_IMAGE.value)
# >>> "https://353sstqmj5.execute-api.us-east-1.amazonaws.com/play1/api/v1/gender-detection/analyzeFacialImage"
```