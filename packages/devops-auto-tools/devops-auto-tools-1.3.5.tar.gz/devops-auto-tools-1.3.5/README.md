# devops-auto-tools
## Hướng dẫn cài đặt:
- Yêu cầu:
    ```
    python >= 3.6
    export PATH="/<custom python bin folder>:$PATH" (thêm vào ~/.zshrc đối với OSX, ~/.bashrc đối với ubuntu/linux càng tốt)
    ```
- Lệnh cài:
  ```bash
  pip install devops-auto-tools
  ```
## Hướng dẫn sử dụng:
### cú pháp:
- Quản lý các cluster eks
  ```bash
  eksm
  ```
- Quản lý các kết nối ssh:
  ```bash
  sshm
  ```
- VPN vào một lớp mạng chỉ định thông qua ssh:
  ```
  jumpm
  ```
## Example:

[Demo jump vào mạng](https://git.rizerssoft.com/rizers/tools/-/blob/main/resources/jumpm-test.mov) | [Demo cách dùng](https://git.rizerssoft.com/rizers/tools/-/blob/main/resources/tutorial.mov)
:-: | :-:
<video src='resources/jumpm-test.mov' width=1000/> | <video src='resources/tutorial.mov' width=1000/>
