# coding=utf-8
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any


class HttpLogger:
    _logger_initialized = False
    request_times = 0
    start_time = None

    @classmethod
    def initialize(cls, caller_file: str, log_dir: str) -> None:
        if cls._logger_initialized:
            return

        # 生成日志文件路径
        log_dir = Path(log_dir)
        log_dir.mkdir(exist_ok=True)

        # 获取调用方文件名
        caller_name = Path(caller_file).stem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"{caller_name}_{timestamp}.log"

        # 配置日志记录器
        logger = logging.getLogger("HttpLogger")
        logger.setLevel(logging.INFO)

        # 文件处理器配置
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        formatter = logging.Formatter(
            fmt='%(asctime)s.%(msecs)03d %(levelname)s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        cls._logger_initialized = True

    @staticmethod
    def _try_pretty_json(content: str) -> str:
        """尝试格式化JSON内容"""
        try:
            json_obj = json.loads(content)
            return json.dumps(json_obj, indent=2, ensure_ascii=False)
        except json.JSONDecodeError:
            return content

    @classmethod
    def log_request(cls, request) -> None:
        """记录HTTP请求日志"""
        cls.start_time = time.time()
        cls.request_times += 1
        try:
            # 解码请求内容
            body = request.content.decode('utf-8') if request.content else ""
            pretty_body = cls._try_pretty_json(body)

            log_data = {
                "request_times": f"{cls.request_times:04d}",
                "type": "REQUEST",
                "url": str(request.url),
                "method": request.method,
                "body": pretty_body
            }
            cls._log_to_file(log_data)
        except Exception as e:
            logging.error(f"记录请求日志失败: {str(e)}")

    @classmethod
    def log_response(cls, response) -> None:
        """记录HTTP响应日志"""
        try:
            # 确保读取响应内容
            response.read()

            spend_time_ms = (time.time() - cls.start_time) * 1000
            # 获取响应内容
            body = response.text if hasattr(response, 'text') else ""
            pretty_body = cls._try_pretty_json(body)

            log_data = {
                "request_times": f"{cls.request_times:04d}",
                "type": "RESPONSE",
                "spend_time_ms": f"{spend_time_ms:.3f}",
                "url": str(response.url),
                "status": response.status_code,
                "body": pretty_body
            }
            cls._log_to_file(log_data)
        except Exception as e:
            logging.error(f"记录响应日志失败: {str(e)}")

    @classmethod
    def _log_to_file(cls, data: Dict[str, Any]) -> None:
        """统一日志记录方法"""
        logger = logging.getLogger("HttpLogger")
        log_msg = "\n".join([f"{k}: {v}" for k, v in data.items()])
        logger.info(f"{log_msg}")
