# Terminal Automation Report

Generated: 2026-07-09

## Run summary
- fixture_root: /tmp/codex_token_usage_terminal_check_report
- sessions: 3
- includes long token total: 1,050,000,000,000

## CLI help (sanity)
- command: env PYTHONPATH=src python -m codex_token_usage --help 
```
exit-code: 0
usage: codex-token-usage [-h] [--codex-home CODEX_HOME]
                         [--format {table,json,csv,graph}] [-c]
                         [--theme {rainbow,transgender,nonbinary,xenogender,agender,queer,genderfluid,bisexual,pansexual,polysexual,omnisexual,omniromantic,gay-men,lesbian,abrosexual,asexual,aromantic,fictosexual,aroace1,aroace2,aroace3,demisexual,autosexual,intergender,greygender,akiosexual,bigender,demigender,demiboy,demigirl,transmasculine,transfeminine,genderfaun,demifaun,genderfae,demifae,neutrois,biromantic1,biromantic2,autoromantic,boyflux2,girlflux,genderflux,nullflux,hypergender,hyperboy,hypergirl,hyperandrogyne,hyperneutrois,finsexual,unlabeled1,unlabeled2,pangender,pangender.contrast,gendernonconforming1,gendernonconforming2,femboy,tomboy,gynesexual,androsexual,gendervoid,voidgirl,voidboy,nonhuman-unity,plural,fraysexual,bear,butch,femme,leather,otter,twink,adipophilia,kenochoric,veldian,solian,lunian,polyam,sapphic,androgyne,interprogress,progress,intersex,old-polyam,equal-rights,drag,pronounfluid,pronounflux,exipronoun,neopronoun,neofluid,genderqueer,cisgender,baker,caninekin,libragender,librafeminine,libramasculine,libraandrogyne,libranonbinary,fluidflux1,fluidflux2,transbian,autism,cenelian,transneutral,enbian,paragender,paraboy,paragirl,paranonbinary,paragenderalt,paraboyalt,paragirlalt,paranonbinaryalt,cupiorose,cupioromantic,cupiosexual,beiyang,burger,throatlozenges,band,petergriffin,rubber,haruhi,queervillain,trans,nonhuman-unit,ynullflux,all,plain,disabled,none}]
                         [--color {auto,always,never}] [--lightness LIGHTNESS]
                         [--since SINCE] [--until UNTIL]
                         [--group-by {date,week,month,hour,session,day,model,cwd,project,folder}]
                         [--top TOP] [--include-zero]
                         [--five-hour-token-limit FIVE_HOUR_TOKEN_LIMIT]
                         [--weekly-token-limit WEEKLY_TOKEN_LIMIT]

Inspect local Codex CLI token usage.

options:
  -h, --help            show this help message and exit
  --codex-home CODEX_HOME
                        Path to the Codex home directory (default: ~/.codex).
  --format {table,json,csv,graph}
                        Print a non-interactive report instead of opening the
                        TUI.
  -c, --config, --setup
                        Open the Pride theme setup wizard and exit.
  --theme {rainbow,transgender,nonbinary,xenogender,agender,queer,genderfluid,bisexual,pansexual,polysexual,omnisexual,omniromantic,gay-men,lesbian,abrosexual,asexual,aromantic,fictosexual,aroace1,aroace2,aroace3,demisexual,autosexual,intergender,greygender,akiosexual,bigender,demigender,demiboy,demigirl,transmasculine,transfeminine,genderfaun,demifaun,genderfae,demifae,neutrois,biromantic1,biromantic2,autoromantic,boyflux2,girlflux,genderflux,nullflux,hypergender,hyperboy,hypergirl,hyperandrogyne,hyperneutrois,finsexual,unlabeled1,unlabeled2,pangender,pangender.contrast,gendernonconforming1,gendernonconforming2,femboy,tomboy,gynesexual,androsexual,gendervoid,voidgirl,voidboy,nonhuman-unity,plural,fraysexual,bear,butch,femme,leather,otter,twink,adipophilia,kenochoric,veldian,solian,lunian,polyam,sapphic,androgyne,interprogress,progress,intersex,old-polyam,equal-rights,drag,pronounfluid,pronounflux,exipronoun,neopronoun,neofluid,genderqueer,cisgender,baker,caninekin,libragender,librafeminine,libramasculine,libraandrogyne,libranonbinary,fluidflux1,fluidflux2,transbian,autism,cenelian,transneutral,enbian,paragender,paraboy,paragirl,paranonbinary,paragenderalt,paraboyalt,paragirlalt,paranonbinaryalt,cupiorose,cupioromantic,cupiosexual,beiyang,burger,throatlozenges,band,petergriffin,rubber,haruhi,queervillain,trans,nonhuman-unit,ynullflux,all,plain,disabled,none}
                        Use a Pride theme preset for this run. Use 'plain' to
                        disable.
  --color {auto,always,never}
                        Control ANSI color for --format graph output (default:
                        auto).
  --lightness LIGHTNESS
                        Override theme lightness for this run with a value
                        from 0 to 1.
  --since SINCE         Include sessions on or after this date (YYYY-MM-DD).
  --until UNTIL         Include sessions on or before this date (YYYY-MM-DD).
  --group-by {date,week,month,hour,session,day,model,cwd,project,folder}
                        Report grouping for non-interactive output. 'day' is
                        an alias for 'date'; 'folder' is an alias for
                        'project'.
  --top TOP             Limit non-interactive output to the top N rows.
  --include-zero        Include sessions with no token_count event or zero
                        tokens.
  --five-hour-token-limit FIVE_HOUR_TOKEN_LIMIT
                        Override the rolling 5-hour token limit for forecast
                        warnings. Use 0 to disable.
  --weekly-token-limit WEEKLY_TOKEN_LIMIT
                        Override the weekly token limit for forecast warnings.
                        Use 0 to disable.
```

## Sweep: format x group-by

## format=table, group-by=date
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format table --group-by date --top 5 
```
exit-code: 0
date        sessions  total              input              output     cached           cached_percent  cache_miss       reasoning
----------  --------  -----------------  -----------------  ---------  ---------------  --------------  ---------------  ---------
2026-06-01         1  1,050,000,000,000  1,000,000,000,000  5,000,000  820,000,000,000           82.0%  180,000,000,000  3,000,000
2026-06-02         1            120,000            100,000     20,000           25,000           25.0%           75,000      2,500
```

## format=table, group-by=week
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format table --group-by week --top 5 
```
exit-code: 0
week      sessions  total              input              output     cached           cached_percent  cache_miss       reasoning
--------  --------  -----------------  -----------------  ---------  ---------------  --------------  ---------------  ---------
2026-W23         2  1,050,000,120,000  1,000,000,100,000  5,020,000  820,000,025,000           82.0%  180,000,075,000  3,002,500
```

## format=table, group-by=month
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format table --group-by month --top 5 
```
exit-code: 0
month    sessions  total              input              output     cached           cached_percent  cache_miss       reasoning
-------  --------  -----------------  -----------------  ---------  ---------------  --------------  ---------------  ---------
2026-06         2  1,050,000,120,000  1,000,000,100,000  5,020,000  820,000,025,000           82.0%  180,000,075,000  3,002,500
```

## format=table, group-by=hour
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format table --group-by hour --top 5 
```
exit-code: 0
hour              sessions  total              input              output     cached           cached_percent  cache_miss       reasoning
----------------  --------  -----------------  -----------------  ---------  ---------------  --------------  ---------------  ---------
2026-06-01 00:00         1  1,050,000,000,000  1,000,000,000,000  5,000,000  820,000,000,000           82.0%  180,000,000,000  3,000,000
2026-06-02 12:00         1            120,000            100,000     20,000           25,000           25.0%           75,000      2,500
```

## format=table, group-by=session
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format table --group-by session --top 5 
```
exit-code: 0
session       title                model    total              input              output     cached           cached_percent  cache_miss       reasoning  updated
------------  -------------------  -------  -----------------  -----------------  ---------  ---------------  --------------  ---------------  ---------  -------------------------
long-session  Long Number Session  gpt-5    1,050,000,000,000  1,000,000,000,000  5,000,000  820,000,000,000           82.0%  180,000,000,000  3,000,000  2026-06-01T00:00:00+00:00
normal-sessi  Normal Session       gpt-4.1            120,000            100,000     20,000           25,000           25.0%           75,000      2,500  2026-06-02T12:00:00+00:00
```

## format=table, group-by=day
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format table --group-by day --top 5 
```
exit-code: 0
date        sessions  total              input              output     cached           cached_percent  cache_miss       reasoning
----------  --------  -----------------  -----------------  ---------  ---------------  --------------  ---------------  ---------
2026-06-01         1  1,050,000,000,000  1,000,000,000,000  5,000,000  820,000,000,000           82.0%  180,000,000,000  3,000,000
2026-06-02         1            120,000            100,000     20,000           25,000           25.0%           75,000      2,500
```

## format=table, group-by=model
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format table --group-by model --top 5 
```
exit-code: 0
model    sessions  total              input              output     cached           cached_percent  cache_miss       reasoning
-------  --------  -----------------  -----------------  ---------  ---------------  --------------  ---------------  ---------
gpt-5           1  1,050,000,000,000  1,000,000,000,000  5,000,000  820,000,000,000           82.0%  180,000,000,000  3,000,000
gpt-4.1         1            120,000            100,000     20,000           25,000           25.0%           75,000      2,500
```

## format=table, group-by=cwd
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format table --group-by cwd --top 5 
```
exit-code: 0
cwd            sessions  total              input              output     cached           cached_percent  cache_miss       reasoning
-------------  --------  -----------------  -----------------  ---------  ---------------  --------------  ---------------  ---------
/project/long         1  1,050,000,000,000  1,000,000,000,000  5,000,000  820,000,000,000           82.0%  180,000,000,000  3,000,000
/project/fast         1            120,000            100,000     20,000           25,000           25.0%           75,000      2,500
```

## format=table, group-by=project
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format table --group-by project --top 5 
```
exit-code: 0
project        sessions  total              input              output     cached           cached_percent  cache_miss       reasoning
-------------  --------  -----------------  -----------------  ---------  ---------------  --------------  ---------------  ---------
/project/long         1  1,050,000,000,000  1,000,000,000,000  5,000,000  820,000,000,000           82.0%  180,000,000,000  3,000,000
/project/fast         1            120,000            100,000     20,000           25,000           25.0%           75,000      2,500
```

## format=table, group-by=folder
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format table --group-by folder --top 5 
```
exit-code: 0
project        sessions  total              input              output     cached           cached_percent  cache_miss       reasoning
-------------  --------  -----------------  -----------------  ---------  ---------------  --------------  ---------------  ---------
/project/long         1  1,050,000,000,000  1,000,000,000,000  5,000,000  820,000,000,000           82.0%  180,000,000,000  3,000,000
/project/fast         1            120,000            100,000     20,000           25,000           25.0%           75,000      2,500
```

## format=json, group-by=date
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format json --group-by date --top 5 
```
exit-code: 0
{
  "codex_home": "/tmp/codex_token_usage_terminal_check_report",
  "group_by": "date",
  "loaded_at": "2026-07-09T09:25:34.743006+00:00",
  "rows": [
    {
      "cwd": null,
      "key": "2026-06-01",
      "model": null,
      "sessions": 1,
      "title": null,
      "tokens": {
        "cache_miss": 180000000000,
        "cached": 820000000000,
        "cached_percent": 82.0,
        "input": 1000000000000,
        "output": 5000000,
        "reasoning": 3000000,
        "total": 1050000000000
      },
      "updated_at": null
    },
    {
      "cwd": null,
      "key": "2026-06-02",
      "model": null,
      "sessions": 1,
      "title": null,
      "tokens": {
        "cache_miss": 75000,
        "cached": 25000,
        "cached_percent": 25.0,
        "input": 100000,
        "output": 20000,
        "reasoning": 2500,
        "total": 120000
      },
      "updated_at": null
    }
  ],
  "sqlite_available": false,
  "sqlite_error": null,
  "totals": {
    "cache_miss": 180000075000,
    "cached": 820000025000,
    "cached_percent": 82.0,
    "input": 1000000100000,
    "output": 5020000,
    "reasoning": 3002500,
    "total": 1050000120000
  }
}
```

## format=json, group-by=week
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format json --group-by week --top 5 
```
exit-code: 0
{
  "codex_home": "/tmp/codex_token_usage_terminal_check_report",
  "group_by": "week",
  "loaded_at": "2026-07-09T09:25:34.804656+00:00",
  "rows": [
    {
      "cwd": null,
      "key": "2026-W23",
      "model": null,
      "sessions": 2,
      "title": null,
      "tokens": {
        "cache_miss": 180000075000,
        "cached": 820000025000,
        "cached_percent": 82.0,
        "input": 1000000100000,
        "output": 5020000,
        "reasoning": 3002500,
        "total": 1050000120000
      },
      "updated_at": null
    }
  ],
  "sqlite_available": false,
  "sqlite_error": null,
  "totals": {
    "cache_miss": 180000075000,
    "cached": 820000025000,
    "cached_percent": 82.0,
    "input": 1000000100000,
    "output": 5020000,
    "reasoning": 3002500,
    "total": 1050000120000
  }
}
```

## format=json, group-by=month
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format json --group-by month --top 5 
```
exit-code: 0
{
  "codex_home": "/tmp/codex_token_usage_terminal_check_report",
  "group_by": "month",
  "loaded_at": "2026-07-09T09:25:34.870308+00:00",
  "rows": [
    {
      "cwd": null,
      "key": "2026-06",
      "model": null,
      "sessions": 2,
      "title": null,
      "tokens": {
        "cache_miss": 180000075000,
        "cached": 820000025000,
        "cached_percent": 82.0,
        "input": 1000000100000,
        "output": 5020000,
        "reasoning": 3002500,
        "total": 1050000120000
      },
      "updated_at": null
    }
  ],
  "sqlite_available": false,
  "sqlite_error": null,
  "totals": {
    "cache_miss": 180000075000,
    "cached": 820000025000,
    "cached_percent": 82.0,
    "input": 1000000100000,
    "output": 5020000,
    "reasoning": 3002500,
    "total": 1050000120000
  }
}
```

## format=json, group-by=hour
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format json --group-by hour --top 5 
```
exit-code: 0
{
  "codex_home": "/tmp/codex_token_usage_terminal_check_report",
  "group_by": "hour",
  "loaded_at": "2026-07-09T09:25:34.933499+00:00",
  "rows": [
    {
      "cwd": null,
      "key": "2026-06-01 00:00",
      "model": null,
      "sessions": 1,
      "title": null,
      "tokens": {
        "cache_miss": 180000000000,
        "cached": 820000000000,
        "cached_percent": 82.0,
        "input": 1000000000000,
        "output": 5000000,
        "reasoning": 3000000,
        "total": 1050000000000
      },
      "updated_at": null
    },
    {
      "cwd": null,
      "key": "2026-06-02 12:00",
      "model": null,
      "sessions": 1,
      "title": null,
      "tokens": {
        "cache_miss": 75000,
        "cached": 25000,
        "cached_percent": 25.0,
        "input": 100000,
        "output": 20000,
        "reasoning": 2500,
        "total": 120000
      },
      "updated_at": null
    }
  ],
  "sqlite_available": false,
  "sqlite_error": null,
  "totals": {
    "cache_miss": 180000075000,
    "cached": 820000025000,
    "cached_percent": 82.0,
    "input": 1000000100000,
    "output": 5020000,
    "reasoning": 3002500,
    "total": 1050000120000
  }
}
```

## format=json, group-by=session
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format json --group-by session --top 5 
```
exit-code: 0
{
  "codex_home": "/tmp/codex_token_usage_terminal_check_report",
  "group_by": "session",
  "loaded_at": "2026-07-09T09:25:34.995002+00:00",
  "rows": [
    {
      "cwd": "/project/long",
      "key": "long-session",
      "model": "gpt-5",
      "sessions": 1,
      "title": "Long Number Session",
      "tokens": {
        "cache_miss": 180000000000,
        "cached": 820000000000,
        "cached_percent": 82.0,
        "input": 1000000000000,
        "output": 5000000,
        "reasoning": 3000000,
        "total": 1050000000000
      },
      "updated_at": "2026-06-01T00:00:00+00:00"
    },
    {
      "cwd": "/project/fast",
      "key": "normal-session",
      "model": "gpt-4.1",
      "sessions": 1,
      "title": "Normal Session",
      "tokens": {
        "cache_miss": 75000,
        "cached": 25000,
        "cached_percent": 25.0,
        "input": 100000,
        "output": 20000,
        "reasoning": 2500,
        "total": 120000
      },
      "updated_at": "2026-06-02T12:00:00+00:00"
    }
  ],
  "sqlite_available": false,
  "sqlite_error": null,
  "totals": {
    "cache_miss": 180000075000,
    "cached": 820000025000,
    "cached_percent": 82.0,
    "input": 1000000100000,
    "output": 5020000,
    "reasoning": 3002500,
    "total": 1050000120000
  }
}
```

## format=json, group-by=day
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format json --group-by day --top 5 
```
exit-code: 0
{
  "codex_home": "/tmp/codex_token_usage_terminal_check_report",
  "group_by": "date",
  "loaded_at": "2026-07-09T09:25:35.065341+00:00",
  "rows": [
    {
      "cwd": null,
      "key": "2026-06-01",
      "model": null,
      "sessions": 1,
      "title": null,
      "tokens": {
        "cache_miss": 180000000000,
        "cached": 820000000000,
        "cached_percent": 82.0,
        "input": 1000000000000,
        "output": 5000000,
        "reasoning": 3000000,
        "total": 1050000000000
      },
      "updated_at": null
    },
    {
      "cwd": null,
      "key": "2026-06-02",
      "model": null,
      "sessions": 1,
      "title": null,
      "tokens": {
        "cache_miss": 75000,
        "cached": 25000,
        "cached_percent": 25.0,
        "input": 100000,
        "output": 20000,
        "reasoning": 2500,
        "total": 120000
      },
      "updated_at": null
    }
  ],
  "sqlite_available": false,
  "sqlite_error": null,
  "totals": {
    "cache_miss": 180000075000,
    "cached": 820000025000,
    "cached_percent": 82.0,
    "input": 1000000100000,
    "output": 5020000,
    "reasoning": 3002500,
    "total": 1050000120000
  }
}
```

## format=json, group-by=model
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format json --group-by model --top 5 
```
exit-code: 0
{
  "codex_home": "/tmp/codex_token_usage_terminal_check_report",
  "group_by": "model",
  "loaded_at": "2026-07-09T09:25:35.133015+00:00",
  "rows": [
    {
      "cwd": null,
      "key": "gpt-5",
      "model": null,
      "sessions": 1,
      "title": null,
      "tokens": {
        "cache_miss": 180000000000,
        "cached": 820000000000,
        "cached_percent": 82.0,
        "input": 1000000000000,
        "output": 5000000,
        "reasoning": 3000000,
        "total": 1050000000000
      },
      "updated_at": null
    },
    {
      "cwd": null,
      "key": "gpt-4.1",
      "model": null,
      "sessions": 1,
      "title": null,
      "tokens": {
        "cache_miss": 75000,
        "cached": 25000,
        "cached_percent": 25.0,
        "input": 100000,
        "output": 20000,
        "reasoning": 2500,
        "total": 120000
      },
      "updated_at": null
    }
  ],
  "sqlite_available": false,
  "sqlite_error": null,
  "totals": {
    "cache_miss": 180000075000,
    "cached": 820000025000,
    "cached_percent": 82.0,
    "input": 1000000100000,
    "output": 5020000,
    "reasoning": 3002500,
    "total": 1050000120000
  }
}
```

## format=json, group-by=cwd
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format json --group-by cwd --top 5 
```
exit-code: 0
{
  "codex_home": "/tmp/codex_token_usage_terminal_check_report",
  "group_by": "cwd",
  "loaded_at": "2026-07-09T09:25:35.205230+00:00",
  "rows": [
    {
      "cwd": null,
      "key": "/project/long",
      "model": null,
      "sessions": 1,
      "title": null,
      "tokens": {
        "cache_miss": 180000000000,
        "cached": 820000000000,
        "cached_percent": 82.0,
        "input": 1000000000000,
        "output": 5000000,
        "reasoning": 3000000,
        "total": 1050000000000
      },
      "updated_at": null
    },
    {
      "cwd": null,
      "key": "/project/fast",
      "model": null,
      "sessions": 1,
      "title": null,
      "tokens": {
        "cache_miss": 75000,
        "cached": 25000,
        "cached_percent": 25.0,
        "input": 100000,
        "output": 20000,
        "reasoning": 2500,
        "total": 120000
      },
      "updated_at": null
    }
  ],
  "sqlite_available": false,
  "sqlite_error": null,
  "totals": {
    "cache_miss": 180000075000,
    "cached": 820000025000,
    "cached_percent": 82.0,
    "input": 1000000100000,
    "output": 5020000,
    "reasoning": 3002500,
    "total": 1050000120000
  }
}
```

## format=json, group-by=project
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format json --group-by project --top 5 
```
exit-code: 0
{
  "codex_home": "/tmp/codex_token_usage_terminal_check_report",
  "group_by": "project",
  "loaded_at": "2026-07-09T09:25:35.275025+00:00",
  "rows": [
    {
      "cwd": null,
      "key": "/project/long",
      "model": null,
      "sessions": 1,
      "title": null,
      "tokens": {
        "cache_miss": 180000000000,
        "cached": 820000000000,
        "cached_percent": 82.0,
        "input": 1000000000000,
        "output": 5000000,
        "reasoning": 3000000,
        "total": 1050000000000
      },
      "updated_at": null
    },
    {
      "cwd": null,
      "key": "/project/fast",
      "model": null,
      "sessions": 1,
      "title": null,
      "tokens": {
        "cache_miss": 75000,
        "cached": 25000,
        "cached_percent": 25.0,
        "input": 100000,
        "output": 20000,
        "reasoning": 2500,
        "total": 120000
      },
      "updated_at": null
    }
  ],
  "sqlite_available": false,
  "sqlite_error": null,
  "totals": {
    "cache_miss": 180000075000,
    "cached": 820000025000,
    "cached_percent": 82.0,
    "input": 1000000100000,
    "output": 5020000,
    "reasoning": 3002500,
    "total": 1050000120000
  }
}
```

## format=json, group-by=folder
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format json --group-by folder --top 5 
```
exit-code: 0
{
  "codex_home": "/tmp/codex_token_usage_terminal_check_report",
  "group_by": "project",
  "loaded_at": "2026-07-09T09:25:35.344345+00:00",
  "rows": [
    {
      "cwd": null,
      "key": "/project/long",
      "model": null,
      "sessions": 1,
      "title": null,
      "tokens": {
        "cache_miss": 180000000000,
        "cached": 820000000000,
        "cached_percent": 82.0,
        "input": 1000000000000,
        "output": 5000000,
        "reasoning": 3000000,
        "total": 1050000000000
      },
      "updated_at": null
    },
    {
      "cwd": null,
      "key": "/project/fast",
      "model": null,
      "sessions": 1,
      "title": null,
      "tokens": {
        "cache_miss": 75000,
        "cached": 25000,
        "cached_percent": 25.0,
        "input": 100000,
        "output": 20000,
        "reasoning": 2500,
        "total": 120000
      },
      "updated_at": null
    }
  ],
  "sqlite_available": false,
  "sqlite_error": null,
  "totals": {
    "cache_miss": 180000075000,
    "cached": 820000025000,
    "cached_percent": 82.0,
    "input": 1000000100000,
    "output": 5020000,
    "reasoning": 3002500,
    "total": 1050000120000
  }
}
```

## format=csv, group-by=date
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format csv --group-by date --top 5 
```
exit-code: 0
date,sessions,total,input,output,cached,cached_percent,cache_miss,reasoning
2026-06-01,1,1050000000000,1000000000000,5000000,820000000000,82.0,180000000000,3000000
2026-06-02,1,120000,100000,20000,25000,25.0,75000,2500
```

## format=csv, group-by=week
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format csv --group-by week --top 5 
```
exit-code: 0
week,sessions,total,input,output,cached,cached_percent,cache_miss,reasoning
2026-W23,2,1050000120000,1000000100000,5020000,820000025000,82.0,180000075000,3002500
```

## format=csv, group-by=month
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format csv --group-by month --top 5 
```
exit-code: 0
month,sessions,total,input,output,cached,cached_percent,cache_miss,reasoning
2026-06,2,1050000120000,1000000100000,5020000,820000025000,82.0,180000075000,3002500
```

## format=csv, group-by=hour
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format csv --group-by hour --top 5 
```
exit-code: 0
hour,sessions,total,input,output,cached,cached_percent,cache_miss,reasoning
2026-06-01 00:00,1,1050000000000,1000000000000,5000000,820000000000,82.0,180000000000,3000000
2026-06-02 12:00,1,120000,100000,20000,25000,25.0,75000,2500
```

## format=csv, group-by=session
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format csv --group-by session --top 5 
```
exit-code: 0
session,title,model,cwd,total,input,output,cached,cached_percent,cache_miss,reasoning,updated
long-session,Long Number Session,gpt-5,/project/long,1050000000000,1000000000000,5000000,820000000000,82.0,180000000000,3000000,2026-06-01T00:00:00+00:00
normal-session,Normal Session,gpt-4.1,/project/fast,120000,100000,20000,25000,25.0,75000,2500,2026-06-02T12:00:00+00:00
```

## format=csv, group-by=day
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format csv --group-by day --top 5 
```
exit-code: 0
date,sessions,total,input,output,cached,cached_percent,cache_miss,reasoning
2026-06-01,1,1050000000000,1000000000000,5000000,820000000000,82.0,180000000000,3000000
2026-06-02,1,120000,100000,20000,25000,25.0,75000,2500
```

## format=csv, group-by=model
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format csv --group-by model --top 5 
```
exit-code: 0
model,sessions,total,input,output,cached,cached_percent,cache_miss,reasoning
gpt-5,1,1050000000000,1000000000000,5000000,820000000000,82.0,180000000000,3000000
gpt-4.1,1,120000,100000,20000,25000,25.0,75000,2500
```

## format=csv, group-by=cwd
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format csv --group-by cwd --top 5 
```
exit-code: 0
cwd,sessions,total,input,output,cached,cached_percent,cache_miss,reasoning
/project/long,1,1050000000000,1000000000000,5000000,820000000000,82.0,180000000000,3000000
/project/fast,1,120000,100000,20000,25000,25.0,75000,2500
```

## format=csv, group-by=project
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format csv --group-by project --top 5 
```
exit-code: 0
project,sessions,total,input,output,cached,cached_percent,cache_miss,reasoning
/project/long,1,1050000000000,1000000000000,5000000,820000000000,82.0,180000000000,3000000
/project/fast,1,120000,100000,20000,25000,25.0,75000,2500
```

## format=csv, group-by=folder
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format csv --group-by folder --top 5 
```
exit-code: 0
project,sessions,total,input,output,cached,cached_percent,cache_miss,reasoning
/project/long,1,1050000000000,1000000000000,5000000,820000000000,82.0,180000000000,3000000
/project/fast,1,120000,100000,20000,25000,25.0,75000,2500
```

## format=graph, group-by=date
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --group-by date --top 5 
```
exit-code: 0
date token usage
2026-06-01 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
2026-06-02 | #                                        total 120,000  cached 25,000  cached% 25.0%  miss 75,000
```

## format=graph, group-by=week
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --group-by week --top 5 
```
exit-code: 0
week token usage
2026-W23 | ######################################## total 1,050,000,120,000  cached 820,000,025,000  cached% 82.0%  miss 180,000,075,000
```

## format=graph, group-by=month
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --group-by month --top 5 
```
exit-code: 0
month token usage
2026-06 | ######################################## total 1,050,000,120,000  cached 820,000,025,000  cached% 82.0%  miss 180,000,075,000
```

## format=graph, group-by=hour
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --group-by hour --top 5 
```
exit-code: 0
hour token usage
2026-06-01 00:00 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
2026-06-02 12:00 | #                                        total 120,000  cached 25,000  cached% 25.0%  miss 75,000
```

## format=graph, group-by=session
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --group-by session --top 5 
```
exit-code: 0
session token usage
long-session   | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
normal-session | #                                        total 120,000  cached 25,000  cached% 25.0%  miss 75,000
```

## format=graph, group-by=day
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --group-by day --top 5 
```
exit-code: 0
date token usage
2026-06-01 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
2026-06-02 | #                                        total 120,000  cached 25,000  cached% 25.0%  miss 75,000
```

## format=graph, group-by=model
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --group-by model --top 5 
```
exit-code: 0
model token usage
gpt-5   | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
gpt-4.1 | #                                        total 120,000  cached 25,000  cached% 25.0%  miss 75,000
```

## format=graph, group-by=cwd
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --group-by cwd --top 5 
```
exit-code: 0
cwd token usage
/project/long | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
/project/fast | #                                        total 120,000  cached 25,000  cached% 25.0%  miss 75,000
```

## format=graph, group-by=project
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --group-by project --top 5 
```
exit-code: 0
project token usage
/project/long | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
/project/fast | #                                        total 120,000  cached 25,000  cached% 25.0%  miss 75,000
```

## format=graph, group-by=folder
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --group-by folder --top 5 
```
exit-code: 0
project token usage
/project/long | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
/project/fast | #                                        total 120,000  cached 25,000  cached% 25.0%  miss 75,000
```

## Settings-level sweep

## include-zero=false default
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format table --group-by session 
```
exit-code: 0
session       title                model    total              input              output     cached           cached_percent  cache_miss       reasoning  updated
------------  -------------------  -------  -----------------  -----------------  ---------  ---------------  --------------  ---------------  ---------  -------------------------
long-session  Long Number Session  gpt-5    1,050,000,000,000  1,000,000,000,000  5,000,000  820,000,000,000           82.0%  180,000,000,000  3,000,000  2026-06-01T00:00:00+00:00
normal-sessi  Normal Session       gpt-4.1            120,000            100,000     20,000           25,000           25.0%           75,000      2,500  2026-06-02T12:00:00+00:00
```

## include-zero=true
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format table --group-by session --include-zero 
```
exit-code: 0
session       title                model    total              input              output     cached           cached_percent  cache_miss       reasoning  updated
------------  -------------------  -------  -----------------  -----------------  ---------  ---------------  --------------  ---------------  ---------  -------------------------
long-session  Long Number Session  gpt-5    1,050,000,000,000  1,000,000,000,000  5,000,000  820,000,000,000           82.0%  180,000,000,000  3,000,000  2026-06-01T00:00:00+00:00
normal-sessi  Normal Session       gpt-4.1            120,000            100,000     20,000           25,000           25.0%           75,000      2,500  2026-06-02T12:00:00+00:00
zero-session  Zero Session         gpt-5                    0                  0          0                0            0.0%                0          0  2026-06-03T15:00:00+00:00
```

## top=2
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format table --group-by session --top 2 
```
exit-code: 0
session       title                model    total              input              output     cached           cached_percent  cache_miss       reasoning  updated
------------  -------------------  -------  -----------------  -----------------  ---------  ---------------  --------------  ---------------  ---------  -------------------------
long-session  Long Number Session  gpt-5    1,050,000,000,000  1,000,000,000,000  5,000,000  820,000,000,000           82.0%  180,000,000,000  3,000,000  2026-06-01T00:00:00+00:00
normal-sessi  Normal Session       gpt-4.1            120,000            100,000     20,000           25,000           25.0%           75,000      2,500  2026-06-02T12:00:00+00:00
```

## date filter
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format table --group-by session --since 2026-06-02 --until 2026-06-02 
```
exit-code: 0
session       title           model    total    input    output  cached  cached_percent  cache_miss  reasoning  updated
------------  --------------  -------  -------  -------  ------  ------  --------------  ----------  ---------  -------------------------
normal-sessi  Normal Session  gpt-4.1  120,000  100,000  20,000  25,000           25.0%      75,000      2,500  2026-06-02T12:00:00+00:00
```

## forecast limits enabled
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format table --group-by week --five-hour-token-limit 50000 --weekly-token-limit 500000 
```
exit-code: 0
week      sessions  total              input              output     cached           cached_percent  cache_miss       reasoning  forecast_status  forecast_remaining  forecast_projected
--------  --------  -----------------  -----------------  ---------  ---------------  --------------  ---------------  ---------  ---------------  ------------------  ------------------
2026-W23         2  1,050,000,120,000  1,000,000,100,000  5,020,000  820,000,025,000           82.0%  180,000,075,000  3,002,500

forecast warnings
window  status  used  limit    remaining  projected  rate/hr
------  ------  ----  -------  ---------  ---------  -------
5h      ok         0   50,000     50,000          0      0.0
week    ok         0  500,000    500,000          0      0.0

usage predictions
period      projected  rate/hr
----------  ---------  -------
next 5h             0      0.0
next day            0      0.0
next week           0      0.0
next month          0      0.0
```

## theme plain graph
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme plain --group-by model 
```
exit-code: 0
model token usage
gpt-5   | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
gpt-4.1 | #                                        total 120,000  cached 25,000  cached% 25.0%  miss 75,000
```

## theme rainbow graph color always
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme rainbow --color always --group-by model 
```
exit-code: 0
model token usage
gpt-5   | [38;5;160m#######[0m[38;5;214m#######[0m[38;5;226m######[0m[38;5;35m#######[0m[38;5;27m#######[0m[38;5;91m######[0m total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
gpt-4.1 | [38;5;160m#[0m                                        total 120,000  cached 25,000  cached% 25.0%  miss 75,000
```

## invalid date range (should fail)
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format table --group-by session --since 2026-06-03 --until 2026-06-01 
```
exit-code: 2
usage: codex-token-usage [-h] [--codex-home CODEX_HOME]
                         [--format {table,json,csv,graph}] [-c]
                         [--theme {rainbow,transgender,nonbinary,xenogender,agender,queer,genderfluid,bisexual,pansexual,polysexual,omnisexual,omniromantic,gay-men,lesbian,abrosexual,asexual,aromantic,fictosexual,aroace1,aroace2,aroace3,demisexual,autosexual,intergender,greygender,akiosexual,bigender,demigender,demiboy,demigirl,transmasculine,transfeminine,genderfaun,demifaun,genderfae,demifae,neutrois,biromantic1,biromantic2,autoromantic,boyflux2,girlflux,genderflux,nullflux,hypergender,hyperboy,hypergirl,hyperandrogyne,hyperneutrois,finsexual,unlabeled1,unlabeled2,pangender,pangender.contrast,gendernonconforming1,gendernonconforming2,femboy,tomboy,gynesexual,androsexual,gendervoid,voidgirl,voidboy,nonhuman-unity,plural,fraysexual,bear,butch,femme,leather,otter,twink,adipophilia,kenochoric,veldian,solian,lunian,polyam,sapphic,androgyne,interprogress,progress,intersex,old-polyam,equal-rights,drag,pronounfluid,pronounflux,exipronoun,neopronoun,neofluid,genderqueer,cisgender,baker,caninekin,libragender,librafeminine,libramasculine,libraandrogyne,libranonbinary,fluidflux1,fluidflux2,transbian,autism,cenelian,transneutral,enbian,paragender,paraboy,paragirl,paranonbinary,paragenderalt,paraboyalt,paragirlalt,paranonbinaryalt,cupiorose,cupioromantic,cupiosexual,beiyang,burger,throatlozenges,band,petergriffin,rubber,haruhi,queervillain,trans,nonhuman-unit,ynullflux,all,plain,disabled,none}]
                         [--color {auto,always,never}] [--lightness LIGHTNESS]
                         [--since SINCE] [--until UNTIL]
                         [--group-by {date,week,month,hour,session,day,model,cwd,project,folder}]
                         [--top TOP] [--include-zero]
                         [--five-hour-token-limit FIVE_HOUR_TOKEN_LIMIT]
                         [--weekly-token-limit WEEKLY_TOKEN_LIMIT]
codex-token-usage: error: --since must be on or before --until
```

## Settings-level sweep (extended)
## no format flag (interactive? should open tui -> likely non-zero)
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --group-by session --since 2026-06-01 --until 2026-06-02 
```
exit-code: 1
[?1049h[22;0;0t[1;24r(B[m[4l[?7h[?1l>Traceback (most recent call last):
  File "/home/foo/miniconda3/lib/python3.13/curses/__init__.py", line 78, in wrapper
    cbreak()
    ~~~~~~^^
_curses.error: cbreak() returned ERR

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "/home/foo/Desktop/Repos/token_usage/src/codex_token_usage/__main__.py", line 5, in <module>
    raise SystemExit(main())
                     ~~~~^^
  File "/home/foo/Desktop/Repos/token_usage/src/codex_token_usage/cli.py", line 182, in main
    return run_tui(
        TuiOptions(
    ...<13 lines>...
        )
    )
  File "/home/foo/Desktop/Repos/token_usage/src/codex_token_usage/tui/app.py", line 43, in run_tui
    curses.wrapper(lambda stdscr: CursesUi(stdscr, state, options).run())
    ~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/foo/miniconda3/lib/python3.13/curses/__init__.py", line 100, in wrapper
    nocbreak()
    ~~~~~~~~^^
_curses.error: nocbreak() returned ERR
```

## color=never graph
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme rainbow --color never --group-by model 
```
exit-code: 0
model token usage
gpt-5   | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
gpt-4.1 | #                                        total 120,000  cached 25,000  cached% 25.0%  miss 75,000
```

## graph color=auto
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme rainbow --color auto --group-by model 
```
exit-code: 0
model token usage
gpt-5   | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
gpt-4.1 | #                                        total 120,000  cached 25,000  cached% 25.0%  miss 75,000
```

## graph color=never
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme rainbow --color never --group-by model 
```
exit-code: 0
model token usage
gpt-5   | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
gpt-4.1 | #                                        total 120,000  cached 25,000  cached% 25.0%  miss 75,000
```

## graph color=always
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme rainbow --color always --group-by model 
```
exit-code: 0
model token usage
gpt-5   | [38;5;160m#######[0m[38;5;214m#######[0m[38;5;226m######[0m[38;5;35m#######[0m[38;5;27m#######[0m[38;5;91m######[0m total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
gpt-4.1 | [38;5;160m#[0m                                        total 120,000  cached 25,000  cached% 25.0%  miss 75,000
```

## invalid color value
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme rainbow --color wrong --group-by model 
```
exit-code: 2
usage: codex-token-usage [-h] [--codex-home CODEX_HOME]
                         [--format {table,json,csv,graph}] [-c]
                         [--theme {rainbow,transgender,nonbinary,xenogender,agender,queer,genderfluid,bisexual,pansexual,polysexual,omnisexual,omniromantic,gay-men,lesbian,abrosexual,asexual,aromantic,fictosexual,aroace1,aroace2,aroace3,demisexual,autosexual,intergender,greygender,akiosexual,bigender,demigender,demiboy,demigirl,transmasculine,transfeminine,genderfaun,demifaun,genderfae,demifae,neutrois,biromantic1,biromantic2,autoromantic,boyflux2,girlflux,genderflux,nullflux,hypergender,hyperboy,hypergirl,hyperandrogyne,hyperneutrois,finsexual,unlabeled1,unlabeled2,pangender,pangender.contrast,gendernonconforming1,gendernonconforming2,femboy,tomboy,gynesexual,androsexual,gendervoid,voidgirl,voidboy,nonhuman-unity,plural,fraysexual,bear,butch,femme,leather,otter,twink,adipophilia,kenochoric,veldian,solian,lunian,polyam,sapphic,androgyne,interprogress,progress,intersex,old-polyam,equal-rights,drag,pronounfluid,pronounflux,exipronoun,neopronoun,neofluid,genderqueer,cisgender,baker,caninekin,libragender,librafeminine,libramasculine,libraandrogyne,libranonbinary,fluidflux1,fluidflux2,transbian,autism,cenelian,transneutral,enbian,paragender,paraboy,paragirl,paranonbinary,paragenderalt,paraboyalt,paragirlalt,paranonbinaryalt,cupiorose,cupioromantic,cupiosexual,beiyang,burger,throatlozenges,band,petergriffin,rubber,haruhi,queervillain,trans,nonhuman-unit,ynullflux,all,plain,disabled,none}]
                         [--color {auto,always,never}] [--lightness LIGHTNESS]
                         [--since SINCE] [--until UNTIL]
                         [--group-by {date,week,month,hour,session,day,model,cwd,project,folder}]
                         [--top TOP] [--include-zero]
                         [--five-hour-token-limit FIVE_HOUR_TOKEN_LIMIT]
                         [--weekly-token-limit WEEKLY_TOKEN_LIMIT]
codex-token-usage: error: argument --color: invalid choice: 'wrong' (choose from auto, always, never)
```

## lightness=0.0
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme rainbow --color always --lightness 0.0 --group-by model 
```
exit-code: 0
model token usage
gpt-5   | [38;5;16m#######[0m[38;5;16m#######[0m[38;5;16m######[0m[38;5;16m#######[0m[38;5;16m#######[0m[38;5;16m######[0m total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
gpt-4.1 | [38;5;16m#[0m                                        total 120,000  cached 25,000  cached% 25.0%  miss 75,000
```

## lightness=0.5
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme rainbow --color always --lightness 0.5 --group-by model 
```
exit-code: 0
model token usage
gpt-5   | [38;5;88m#######[0m[38;5;130m#######[0m[38;5;136m######[0m[38;5;22m#######[0m[38;5;25m#######[0m[38;5;53m######[0m total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
gpt-4.1 | [38;5;88m#[0m                                        total 120,000  cached 25,000  cached% 25.0%  miss 75,000
```

## lightness=1.0
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme rainbow --color always --lightness 1.0 --group-by model 
```
exit-code: 0
model token usage
gpt-5   | [38;5;160m#######[0m[38;5;214m#######[0m[38;5;226m######[0m[38;5;35m#######[0m[38;5;27m#######[0m[38;5;91m######[0m total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
gpt-4.1 | [38;5;160m#[0m                                        total 120,000  cached 25,000  cached% 25.0%  miss 75,000
```

## invalid lightness out of range
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme rainbow --lightness 1.5 --group-by model 
```
exit-code: 2
usage: codex-token-usage [-h] [--codex-home CODEX_HOME]
                         [--format {table,json,csv,graph}] [-c]
                         [--theme {rainbow,transgender,nonbinary,xenogender,agender,queer,genderfluid,bisexual,pansexual,polysexual,omnisexual,omniromantic,gay-men,lesbian,abrosexual,asexual,aromantic,fictosexual,aroace1,aroace2,aroace3,demisexual,autosexual,intergender,greygender,akiosexual,bigender,demigender,demiboy,demigirl,transmasculine,transfeminine,genderfaun,demifaun,genderfae,demifae,neutrois,biromantic1,biromantic2,autoromantic,boyflux2,girlflux,genderflux,nullflux,hypergender,hyperboy,hypergirl,hyperandrogyne,hyperneutrois,finsexual,unlabeled1,unlabeled2,pangender,pangender.contrast,gendernonconforming1,gendernonconforming2,femboy,tomboy,gynesexual,androsexual,gendervoid,voidgirl,voidboy,nonhuman-unity,plural,fraysexual,bear,butch,femme,leather,otter,twink,adipophilia,kenochoric,veldian,solian,lunian,polyam,sapphic,androgyne,interprogress,progress,intersex,old-polyam,equal-rights,drag,pronounfluid,pronounflux,exipronoun,neopronoun,neofluid,genderqueer,cisgender,baker,caninekin,libragender,librafeminine,libramasculine,libraandrogyne,libranonbinary,fluidflux1,fluidflux2,transbian,autism,cenelian,transneutral,enbian,paragender,paraboy,paragirl,paranonbinary,paragenderalt,paraboyalt,paragirlalt,paranonbinaryalt,cupiorose,cupioromantic,cupiosexual,beiyang,burger,throatlozenges,band,petergriffin,rubber,haruhi,queervillain,trans,nonhuman-unit,ynullflux,all,plain,disabled,none}]
                         [--color {auto,always,never}] [--lightness LIGHTNESS]
                         [--since SINCE] [--until UNTIL]
                         [--group-by {date,week,month,hour,session,day,model,cwd,project,folder}]
                         [--top TOP] [--include-zero]
                         [--five-hour-token-limit FIVE_HOUR_TOKEN_LIMIT]
                         [--weekly-token-limit WEEKLY_TOKEN_LIMIT]
codex-token-usage: error: argument --lightness: lightness must be from 0 to 1
```

## forecast limits zero disabled
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format table --group-by week --five-hour-token-limit 0 --weekly-token-limit 0 
```
exit-code: 0
week      sessions  total              input              output     cached           cached_percent  cache_miss       reasoning
--------  --------  -----------------  -----------------  ---------  ---------------  --------------  ---------------  ---------
2026-W23         2  1,050,000,120,000  1,000,000,100,000  5,020,000  820,000,025,000           82.0%  180,000,075,000  3,002,500
```

## top=0
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format table --group-by session --top 0 
```
exit-code: 0
session       title                model    total              input              output     cached           cached_percent  cache_miss       reasoning  updated
------------  -------------------  -------  -----------------  -----------------  ---------  ---------------  --------------  ---------------  ---------  -------------------------
long-session  Long Number Session  gpt-5    1,050,000,000,000  1,000,000,000,000  5,000,000  820,000,000,000           82.0%  180,000,000,000  3,000,000  2026-06-01T00:00:00+00:00
normal-sessi  Normal Session       gpt-4.1            120,000            100,000     20,000           25,000           25.0%           75,000      2,500  2026-06-02T12:00:00+00:00
```

## top=1 include-zero+graph
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --group-by session --include-zero --top 1 
```
exit-code: 0
session token usage
long-session | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## empty codex home
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_empty --format table 
```
exit-code: 0
date  sessions  total  input  output  cached  cached_percent  cache_miss  reasoning
----  --------  -----  -----  ------  ------  --------------  ----------  ---------
```

## invalid forecast negative values
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format table --group-by week --five-hour-token-limit -1 --weekly-token-limit -1 
```
exit-code: 2
usage: codex-token-usage [-h] [--codex-home CODEX_HOME]
                         [--format {table,json,csv,graph}] [-c]
                         [--theme {rainbow,transgender,nonbinary,xenogender,agender,queer,genderfluid,bisexual,pansexual,polysexual,omnisexual,omniromantic,gay-men,lesbian,abrosexual,asexual,aromantic,fictosexual,aroace1,aroace2,aroace3,demisexual,autosexual,intergender,greygender,akiosexual,bigender,demigender,demiboy,demigirl,transmasculine,transfeminine,genderfaun,demifaun,genderfae,demifae,neutrois,biromantic1,biromantic2,autoromantic,boyflux2,girlflux,genderflux,nullflux,hypergender,hyperboy,hypergirl,hyperandrogyne,hyperneutrois,finsexual,unlabeled1,unlabeled2,pangender,pangender.contrast,gendernonconforming1,gendernonconforming2,femboy,tomboy,gynesexual,androsexual,gendervoid,voidgirl,voidboy,nonhuman-unity,plural,fraysexual,bear,butch,femme,leather,otter,twink,adipophilia,kenochoric,veldian,solian,lunian,polyam,sapphic,androgyne,interprogress,progress,intersex,old-polyam,equal-rights,drag,pronounfluid,pronounflux,exipronoun,neopronoun,neofluid,genderqueer,cisgender,baker,caninekin,libragender,librafeminine,libramasculine,libraandrogyne,libranonbinary,fluidflux1,fluidflux2,transbian,autism,cenelian,transneutral,enbian,paragender,paraboy,paragirl,paranonbinary,paragenderalt,paraboyalt,paragirlalt,paranonbinaryalt,cupiorose,cupioromantic,cupiosexual,beiyang,burger,throatlozenges,band,petergriffin,rubber,haruhi,queervillain,trans,nonhuman-unit,ynullflux,all,plain,disabled,none}]
                         [--color {auto,always,never}] [--lightness LIGHTNESS]
                         [--since SINCE] [--until UNTIL]
                         [--group-by {date,week,month,hour,session,day,model,cwd,project,folder}]
                         [--top TOP] [--include-zero]
                         [--five-hour-token-limit FIVE_HOUR_TOKEN_LIMIT]
                         [--weekly-token-limit WEEKLY_TOKEN_LIMIT]
codex-token-usage: error: argument --five-hour-token-limit: token limit must not be negative
```

## theme value loop

## --theme=rainbow
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme rainbow --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=transgender
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme transgender --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=nonbinary
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme nonbinary --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=xenogender
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme xenogender --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=agender
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme agender --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=queer
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme queer --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=genderfluid
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme genderfluid --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=bisexual
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme bisexual --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=pansexual
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme pansexual --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=polysexual
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme polysexual --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=omnisexual
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme omnisexual --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=omniromantic
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme omniromantic --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=gay-men
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme gay-men --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=lesbian
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme lesbian --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=abrosexual
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme abrosexual --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=asexual
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme asexual --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=aromantic
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme aromantic --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=fictosexual
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme fictosexual --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=aroace1
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme aroace1 --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=aroace2
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme aroace2 --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=aroace3
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme aroace3 --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=demisexual
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme demisexual --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=autosexual
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme autosexual --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=intergender
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme intergender --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=greygender
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme greygender --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=akiosexual
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme akiosexual --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=bigender
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme bigender --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=demigender
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme demigender --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=demiboy
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme demiboy --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=demigirl
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme demigirl --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=transmasculine
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme transmasculine --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=transfeminine
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme transfeminine --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=genderfaun
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme genderfaun --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=demifaun
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme demifaun --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=genderfae
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme genderfae --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=demifae
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme demifae --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=neutrois
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme neutrois --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=biromantic1
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme biromantic1 --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=biromantic2
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme biromantic2 --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=autoromantic
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme autoromantic --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=boyflux2
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme boyflux2 --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=girlflux
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme girlflux --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=genderflux
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme genderflux --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=nullflux
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme nullflux --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=hypergender
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme hypergender --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=hyperboy
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme hyperboy --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=hypergirl
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme hypergirl --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=hyperandrogyne
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme hyperandrogyne --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=hyperneutrois
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme hyperneutrois --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=finsexual
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme finsexual --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=unlabeled1
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme unlabeled1 --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=unlabeled2
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme unlabeled2 --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=pangender
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme pangender --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=pangender.contrast
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme pangender.contrast --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=gendernonconforming1
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme gendernonconforming1 --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=gendernonconforming2
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme gendernonconforming2 --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=femboy
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme femboy --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=tomboy
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme tomboy --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=gynesexual
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme gynesexual --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=androsexual
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme androsexual --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=gendervoid
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme gendervoid --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=voidgirl
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme voidgirl --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=voidboy
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme voidboy --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=nonhuman-unity
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme nonhuman-unity --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=plural
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme plural --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=fraysexual
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme fraysexual --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=bear
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme bear --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=butch
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme butch --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=femme
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme femme --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=leather
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme leather --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=otter
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme otter --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=twink
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme twink --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=adipophilia
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme adipophilia --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=kenochoric
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme kenochoric --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=veldian
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme veldian --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=solian
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme solian --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=lunian
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme lunian --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=polyam
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme polyam --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=sapphic
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme sapphic --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=androgyne
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme androgyne --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=interprogress
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme interprogress --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=progress
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme progress --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=intersex
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme intersex --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=old-polyam
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme old-polyam --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=equal-rights
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme equal-rights --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=drag
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme drag --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=pronounfluid
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme pronounfluid --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=pronounflux
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme pronounflux --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=exipronoun
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme exipronoun --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=neopronoun
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme neopronoun --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=neofluid
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme neofluid --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=genderqueer
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme genderqueer --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=cisgender
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme cisgender --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=baker
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme baker --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=caninekin
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme caninekin --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=libragender
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme libragender --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=librafeminine
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme librafeminine --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=libramasculine
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme libramasculine --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=libraandrogyne
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme libraandrogyne --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=libranonbinary
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme libranonbinary --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=fluidflux1
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme fluidflux1 --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=fluidflux2
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme fluidflux2 --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=transbian
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme transbian --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=autism
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme autism --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=cenelian
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme cenelian --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=transneutral
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme transneutral --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=enbian
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme enbian --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=paragender
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme paragender --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=paraboy
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme paraboy --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=paragirl
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme paragirl --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=paranonbinary
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme paranonbinary --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=paragenderalt
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme paragenderalt --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=paraboyalt
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme paraboyalt --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=paragirlalt
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme paragirlalt --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=paranonbinaryalt
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme paranonbinaryalt --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=cupiorose
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme cupiorose --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=cupioromantic
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme cupioromantic --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=cupiosexual
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme cupiosexual --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=beiyang
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme beiyang --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=burger
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme burger --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=throatlozenges
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme throatlozenges --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=band
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme band --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=petergriffin
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme petergriffin --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=rubber
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme rubber --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=haruhi
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme haruhi --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=queervillain
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme queervillain --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=trans
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme trans --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=nonhuman-unit
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme nonhuman-unit --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=ynullflux
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme ynullflux --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=all
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme all --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=plain
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme plain --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=disabled
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme disabled --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

## --theme=none
- command: env PYTHONPATH=src python -m codex_token_usage --codex-home /tmp/codex_token_usage_terminal_check_report --format graph --theme none --group-by model --top 1
```
exit-code: 0
model token usage
gpt-5 | ######################################## total 1,050,000,000,000  cached 820,000,000,000  cached% 82.0%  miss 180,000,000,000
```

