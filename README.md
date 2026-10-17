# 13CIT TabManager

## Pre compiled binaries
should be in the releases tab assuming i remembered to do this... who knows

> [!NOTE] 
> I have used inter across this project, please install the font for correct rendering

https://fonts.google.com/specimen/Inter

## Linux Setup
(ensure python/pip is setup correctly prior to running)

``` 
pip install -r requirements.txt
python main.py 
```

### or through venv (preferred)

``` 
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py 
```

## Windows Setup
(ensure python/pip is setup correctly prior to running. commands below may be different depending on your python setup)

in my case, i had to also install this (i dont understand how devs manage with this BS on windows.. lol)

https://aka.ms/vs/stable/vs_BuildTools.exe

```
python -m pip install -r requirements.txt
python main.py
```

### or through venv (preferred)
```
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python main.py
```

# 

# TODO
- ✅ detect path (platform dependent (e.g /usr/bin/firefox, C:\Program Files (x86)\Google\Chrome\Application\chrome.exe))
- ✅ get basic tab execution/groups done
- tab group creation GUI
- custom lists n stuff
- allow users to select browser from dropdown
- allow users to select profile? from dropdown

# LATER
- calendar LATER - work on tab groups first. ICS stuff hold for now
- ui improvements
- everything else