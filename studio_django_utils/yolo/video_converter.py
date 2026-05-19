#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频转换工具类
用于将视频转换为H.264编码的MP4格式，确保浏览器兼容性
"""

import os
import subprocess
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class VideoConverter:
    """视频格式转换工具类"""
    
    def __init__(self):
        """初始化视频转换器"""
        self.ffmpeg_available = self._check_ffmpeg()
    
    def _check_ffmpeg(self) -> bool:
        """
        检查FFmpeg是否可用
        
        Returns:
            bool: FFmpeg是否可用
        """
        try:
            result = subprocess.run(
                ['ffmpeg', '-version'], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            logger.warning("FFmpeg未安装或不可用")
            return False
    
    def get_video_info(self, video_path: str) -> Optional[Dict[str, Any]]:
        """
        获取视频信息
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            Dict: 视频信息字典，包含编码格式、分辨率、时长等
        """
        if not self.ffmpeg_available:
            logger.error("FFmpeg不可用，无法获取视频信息")
            return None
        
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', '-show_streams', video_path
            ]
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            
            if result.returncode != 0:
                logger.error(f"获取视频信息失败: {result.stderr}")
                return None
            
            info = json.loads(result.stdout)
            
            # 查找视频流
            video_stream = None
            for stream in info.get('streams', []):
                if stream.get('codec_type') == 'video':
                    video_stream = stream
                    break
            
            if not video_stream:
                logger.error("未找到视频流")
                return None
            
            return {
                'codec': video_stream.get('codec_name', 'unknown'),
                'width': video_stream.get('width', 0),
                'height': video_stream.get('height', 0),
                'duration': float(info.get('format', {}).get('duration', 0)),
                'size': os.path.getsize(video_path) if os.path.exists(video_path) else 0
            }
            
        except Exception as e:
            logger.error(f"获取视频信息时出错: {str(e)}")
            return None
    
    def is_h264_compatible(self, video_path: str) -> bool:
        """
        检查视频是否已经是H.264编码
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            bool: 是否为H.264编码
        """
        video_info = self.get_video_info(video_path)
        if not video_info:
            return False
        
        return video_info.get('codec', '').lower() == 'h264'
    
    def convert_to_h264(self, input_path: str, output_path: Optional[str] = None, 
                       quality: str = 'medium', overwrite: bool = True) -> Optional[str]:
        """
        将视频转换为H.264编码的MP4格式
        
        Args:
            input_path: 输入视频文件路径
            output_path: 输出视频文件路径（可选）
            quality: 质量设置 ('high', 'medium', 'low')
            overwrite: 是否覆盖已存在的文件
            
        Returns:
            str: 转换后的文件路径，失败返回None
        """
        if not self.ffmpeg_available:
            logger.error("FFmpeg不可用，无法进行视频转换")
            return None
        
        input_path = Path(input_path)
        
        if not input_path.exists():
            logger.error(f"输入文件不存在: {input_path}")
            return None
        
        # 检查是否已经是H.264格式
        if self.is_h264_compatible(str(input_path)):
            logger.info(f"视频已经是H.264格式: {input_path}")
            return str(input_path)
        
        # 生成输出文件路径
        if output_path is None:
            output_path = input_path.parent / f"{input_path.stem}_h264.mp4"
        else:
            output_path = Path(output_path)
        
        # 检查输出文件是否已存在
        if output_path.exists() and not overwrite:
            logger.info(f"输出文件已存在: {output_path}")
            return str(output_path)
        
        # 设置质量参数
        quality_settings = {
            'high': {'crf': '18', 'preset': 'slow'},
            'medium': {'crf': '23', 'preset': 'medium'},
            'low': {'crf': '28', 'preset': 'fast'}
        }
        
        settings = quality_settings.get(quality, quality_settings['medium'])
        
        # 构建FFmpeg命令
        cmd = [
            'ffmpeg',
            '-i', str(input_path),
            '-c:v', 'libx264',          # 使用H.264编码器
            '-crf', settings['crf'],     # 质量设置
            '-preset', settings['preset'], # 编码速度预设
            '-c:a', 'aac',              # 音频编码器
            '-b:a', '128k',             # 音频比特率
            '-movflags', '+faststart',   # 优化网络播放
            '-y' if overwrite else '-n', # 覆盖或跳过已存在文件
            str(output_path)
        ]
        
        try:
            logger.info(f"开始转换视频: {input_path} -> {output_path}")
            
            # 执行转换
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            
            if result.returncode == 0:
                if output_path.exists():
                    logger.info(f"视频转换成功: {output_path}")
                    
                    # 验证转换结果
                    if self.is_h264_compatible(str(output_path)):
                        return str(output_path)
                    else:
                        logger.error("转换完成但格式验证失败")
                        return None
                else:
                    logger.error("转换完成但输出文件未生成")
                    return None
            else:
                logger.error(f"视频转换失败: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            logger.error("视频转换超时")
            return None
        except Exception as e:
            logger.error(f"视频转换过程中出错: {str(e)}")
            return None
    
    def ensure_h264_format(self, video_path: str, quality: str = 'medium') -> str:
        """
        确保视频为H.264格式，如果不是则自动转换
        
        Args:
            video_path: 视频文件路径
            quality: 转换质量设置
            
        Returns:
            str: H.264格式的视频文件路径
        """
        if self.is_h264_compatible(video_path):
            return video_path
        
        converted_path = self.convert_to_h264(video_path, quality=quality)
        return converted_path if converted_path else video_path
    
    def get_conversion_status(self) -> Dict[str, Any]:
        """
        获取转换器状态信息
        
        Returns:
            Dict: 状态信息
        """
        return {
            'ffmpeg_available': self.ffmpeg_available,
            'supported_formats': ['mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv'] if self.ffmpeg_available else [],
            'output_format': 'H.264 MP4'
        }

# 创建全局实例
video_converter = VideoConverter()