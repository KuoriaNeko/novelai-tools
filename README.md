# Novel AI Tools

Simple Novel AI image generation tool

## How to get access token

- Login to [Novel AI](https://novelai.net)
- Press `F12` to open developer tool and switch to `Console` tab
- Ctrl + C, Ctrl + V, Enter
  ```javascript
  console.log(JSON.parse(localStorage.session).auth_token)
  ```

## Usage

- Clone or download this repo
- Install requirements
- cp/mv `config.example.yml` to `config.yml` and edit it
- Prepare your prompts, refer to `prompts.example.yml`
- Run

## Credits

- [nai3_train](https://github.com/wochenlong/nai3_train)