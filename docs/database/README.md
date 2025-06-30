# Documentation database

## Project Structure

### `client.py`

This file defines the **DB application** with all its attributes and courotines such as `create_tables`, `insert_problem` and `check_if_problem_exists`.

The database is currently only used for creating relations between a [Checkmk](/docs/checkmk/README.md) problem id and a [SDP](/docs/sdp/README.md) request id.
