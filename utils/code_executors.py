import subprocess
import shutil
from configs.configs import image_map
from utils.utils import generate_unique_dir
import os

def run_python(code):
    # 构建docker命令
    docker_command = [
        "docker", "run", "--rm", "-i", image_map['Python'], "python", "-c", code
    ]

    try:
        # 执行docker命令
        result = subprocess.run(docker_command, capture_output=True, text=True, check=True)
        # 返回标准输出
        return {"stdout": result.stdout}
    except subprocess.CalledProcessError as e:
        # 如果命令执行失败，返回错误信息
        return {"error": e.stderr}
    except Exception as e:
        return {"error": e}

def run_c(code):
    # 建立临时文件夹用于存储编译产生的文件
    tmp_dir = generate_unique_dir()

    try:
        # 运行编译命令
        compile_command = f"docker run --rm -i -v {tmp_dir}:/tmp {image_map['C']} gcc -x c -o /tmp/program -"
        result = subprocess.run(compile_command, input=code, capture_output=True, text=True, shell=True, check=True)

        # 运行编译后的程序
        run_command = f"docker run --rm -i -v {tmp_dir}:/tmp {image_map['C']} /tmp/program"
        result = subprocess.run(run_command, capture_output=True, text=True, shell=True, check=True)

        return {"stdout": result.stdout}

    except subprocess.CalledProcessError as e:
        # 如果命令执行失败，返回错误信息
        return {"error": e.stderr}

    except Exception as e:
        return {"error": str(e)}

    finally:
        # 删除临时文件夹
        shutil.rmtree(tmp_dir)

def run_cpp(code):
    # 建立临时文件夹用于存储编译产生的文件
    tmp_dir = generate_unique_dir()

    try:
        # 运行编译命令
        compile_command = f"docker run --rm -i -v {tmp_dir}:/tmp {image_map['C++']} g++ -x c++ -o /tmp/program -"
        result = subprocess.run(compile_command, input=code, capture_output=True, text=True, shell=True, check=True)

        # 运行编译后的程序
        run_command = f"docker run --rm -i -v {tmp_dir}:/tmp {image_map['C++']} /tmp/program"
        result = subprocess.run(run_command, capture_output=True, text=True, shell=True, check=True)

        return {"stdout": result.stdout}

    except subprocess.CalledProcessError as e:
        # 捕获命令执行失败的错误并返回
        return {"error": e.stderr}

    except Exception as e:
        # 捕获其他异常错误
        return {"error": str(e)}

    finally:
        # 删除临时文件夹
        shutil.rmtree(tmp_dir)

def run_java(code):
    # 建立临时文件夹用于存储编译产生的文件
    tmp_dir = generate_unique_dir()

    try:
        # 将 Java 代码保存为 Main.java 文件
        java_file_path = os.path.join(tmp_dir, "Main.java")
        with open(java_file_path, "w") as java_file:
            java_file.write(code)

        # 运行编译命令
        compile_command = f"docker run --rm -i -v {tmp_dir}:/tmp -w /tmp {image_map['Java']} javac Main.java"
        result = subprocess.run(compile_command, input=code, capture_output=True, text=True, shell=True, check=True)

        # 运行编译后的程序
        run_command = f"docker run --rm -i -v {tmp_dir}:/tmp -w /tmp {image_map['Java']} java Main"
        result = subprocess.run(run_command, capture_output=True, text=True, shell=True, check=True)

        return {"stdout": result.stdout}

    except subprocess.CalledProcessError as e:
        # 捕获命令执行失败的错误并返回
        return {"error": e.stderr}

    except Exception as e:
        # 捕获其他异常错误
        return {"error": str(e)}

    finally:
        # 删除临时文件夹
        shutil.rmtree(tmp_dir)

def run_rust(code):
    # 建立临时文件夹用于存储编译产生的文件
    tmp_dir = generate_unique_dir()

    try:
        # 创建一个Rust源文件
        rust_file_path = os.path.join(tmp_dir, 'main.rs')
        with open(rust_file_path, 'w') as f:
            f.write(code)

        # 运行编译命令
        compile_command = f"docker run --rm -i -v {tmp_dir}:/tmp {image_map['Rust']} rustc /tmp/main.rs -o /tmp/program"
        result = subprocess.run(compile_command, capture_output=True, text=True, shell=True)

        # 检查编译过程中的错误
        if result.returncode != 0:
            return {"error": result.stderr}

        # 运行编译后的程序
        run_command = f"docker run --rm -i -v {tmp_dir}:/tmp {image_map['Rust']} /tmp/program"
        result = subprocess.run(run_command, capture_output=True, text=True, shell=True)

        # 检查运行时错误
        if result.returncode != 0:
            return {"error": result.stderr}

        # 返回程序的标准输出
        return {"stdout": result.stdout}

    except subprocess.CalledProcessError as e:
        # 捕获命令执行失败的错误并返回
        return {"error": e.stderr}

    except Exception as e:
        # 捕获其他异常错误
        return {"error": str(e)}

    finally:
        # 删除临时文件夹
        shutil.rmtree(tmp_dir)

def run_go(code):
    # 建立临时文件夹用于存储代码文件
    tmp_dir = generate_unique_dir()

    try:
        # 将 Go 代码写入临时文件
        code_file = os.path.join(tmp_dir, 'main.go')
        with open(code_file, 'w') as f:
            f.write(code)

        # 运行 Go 代码（使用 go run 命令直接运行 main.go）
        run_command = f"docker run --rm -i -v {tmp_dir}:/tmp {image_map['Go']} go run /tmp/main.go"
        result = subprocess.run(run_command, capture_output=True, text=True, shell=True, check=True)

        # 返回程序的标准输出
        return {"stdout": result.stdout}

    except subprocess.CalledProcessError as e:
        # 如果命令执行失败，返回错误信息
        return {"error": e.stderr}

    except Exception as e:
        return {"error": str(e)}