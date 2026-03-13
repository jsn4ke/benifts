"""Web 服务器启动脚本

运行此脚本来启动 B2 Web 界面。

使用方法:
    python run_web.py

启动后访问: http://localhost:5000
"""

import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("B2 Web 服务器")
    print("=" * 60 + "\n")

    try:
        from src.web import run_app

        print("启动 Web 服务器...")
        print("访问地址: http://localhost:5000")
        print("按 Ctrl+C 停止服务器\n")

        run_app(host="0.0.0.0", port=5000, debug=True)

    except KeyboardInterrupt:
        print("\n\n服务器已停止")
    except ImportError as e:
        logger.error(f"导入失败: {e}")
        print("\n错误: 请确保已安装所有依赖")
        print("运行: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        logger.error(f"服务器启动失败: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
