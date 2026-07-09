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

