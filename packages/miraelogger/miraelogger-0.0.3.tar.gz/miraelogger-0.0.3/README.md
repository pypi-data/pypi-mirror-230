# miraelogger
This is just my custom logger for me.

---

## GitHub Repository Link
[**mirealogger** GitHub Repository Link](https://github.com/milktea0614/miraelogger)

## PyPI Link
[miraelogger pypi](https://pypi.org/project/miraelogger/)

---

## How to use

### 1. install the miraelogger
```pip install miraelogger```

### 2. import miraelogger
```from miraelogger import Logger```

### 3. init object
<details>
<summary>If you want to print log only</summary>
<div>

```my_logger = Logger()```

</div>
</details>
&nbsp;
<details>
<summary>If you want to print log and save log</summary>
<div>

```my_logger = Logger(log_file="input your path")```

</div>
</details>
&nbsp;
<details>
<summary>If you want to print log and save log. Also, not want to delete an old log. </summary>
<div>

The logs which are older than 14 days is remove.

```my_logger = Logger(log_file="input your path", delete_old_log=False)```

</div>
</details>
