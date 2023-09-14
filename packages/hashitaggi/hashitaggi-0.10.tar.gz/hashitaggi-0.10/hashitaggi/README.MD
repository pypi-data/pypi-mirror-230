# Get related hashtags

## Tested against Windows 10 / Python 3.10 / Anaconda

### pip install hashitaggi


```python
from hashitaggi import get_hashtags
df = get_hashtags(
	hashtags=['jiujitsu', 'bjj'],
	opera_browser_exe=r"C:\Program Files\Opera GX\opera.exe",
	opera_driver_exe=r"C:\ProgramData\anaconda3\envs\dfdir\operadriver.exe",
	userdir=r"C:\operabrowserprofile2",
)
print(df)

```