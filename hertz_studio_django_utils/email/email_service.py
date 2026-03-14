from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils.html import strip_tags
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """
    邮件发送服务类
    提供统一的邮件发送接口
    """
    
    @staticmethod
    def send_email(
        recipient_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        from_email: Optional[str] = None
    ) -> bool:
        """
        发送邮件
        
        Args:
            recipient_email: 收件人邮箱
            subject: 邮件主题
            html_content: HTML内容
            text_content: 纯文本内容（可选）
            from_email: 发件人邮箱（可选）
            
        Returns:
            bool: 发送是否成功
        """
        try:
            # 检查邮件配置
            if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
                logger.warning("邮件配置不完整，使用控制台输出模式")
                logger.info(f"收件人: {recipient_email}")
                logger.info(f"主题: {subject}")
                logger.info(f"内容: {text_content or strip_tags(html_content)[:200]}...")
                return True
            
            # 如果没有提供纯文本内容，从HTML中提取
            if not text_content:
                text_content = strip_tags(html_content)
            
            # 创建邮件
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=from_email or settings.DEFAULT_FROM_EMAIL,
                to=[recipient_email]
            )
            
            # 添加HTML内容
            email.attach_alternative(html_content, "text/html")
            
            # 发送邮件
            email.send()
            logger.info(f"邮件发送成功: {recipient_email}")
            return True
            
        except Exception as e:
            logger.error(f"邮件发送失败: {str(e)}")
            return False
    
    @staticmethod
    def send_verification_code(
        recipient_email: str,
        recipient_name: str,
        verification_code: str,
        code_type: str = 'register'
    ) -> bool:
        """
        发送验证码邮件
        
        Args:
            recipient_email: 收件人邮箱
            recipient_name: 收件人姓名
            verification_code: 验证码
            code_type: 验证码类型（register/reset_password）
            
        Returns:
            bool: 发送是否成功
        """
        # 根据类型生成邮件内容
        email_content = EmailService._generate_verification_email_content(
            recipient_name, verification_code, code_type
        )
        
        return EmailService.send_email(
            recipient_email=recipient_email,
            subject=email_content['subject'],
            html_content=email_content['html_content'],
            text_content=email_content['text_content']
        )
    
    @staticmethod
    def _generate_verification_email_content(
        recipient_name: str,
        verification_code: str,
        code_type: str
    ) -> Dict[str, str]:
        """
        生成验证码邮件内容
        
        Args:
            recipient_name: 收件人姓名
            verification_code: 验证码
            code_type: 验证码类型
            
        Returns:
            Dict[str, str]: 包含subject, html_content, text_content的字典
        """
        if code_type == 'register':
            subject = '🔐 注册验证码 - Hertz Server Django'
            title = '注册验证码'
            description = '感谢您注册 Hertz Server Django！请使用以下验证码完成注册：'
        elif code_type == 'reset_password':
            subject = '🔐 密码重置验证码 - Hertz Server Django'
            title = '密码重置验证码'
            description = '您正在重置密码，请使用以下验证码完成操作：'
        else:
            subject = '🔐 邮箱验证码 - Hertz Server Django'
            title = '邮箱验证码'
            description = '请使用以下验证码完成验证：'
        
        html_content = f'''
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: #28a745; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0;">
                    <h1 style="margin: 0; font-size: 24px;">🔐 {title}</h1>
                </div>
                <div style="background: white; padding: 30px; border: 1px solid #e1e5e9; border-radius: 0 0 10px 10px;">
                    <p style="font-size: 16px;">亲爱的 <strong>{recipient_name}</strong>，</p>
                    <p>{description}</p>
                    <div style="text-align: center; margin: 40px 0;">
                        <div style="background: #f8f9fa; border: 2px dashed #28a745; padding: 20px; border-radius: 10px; display: inline-block;">
                            <span style="font-size: 32px; font-weight: bold; color: #28a745; letter-spacing: 5px;">{verification_code}</span>
                        </div>
                    </div>
                    <p style="color: #666; font-size: 14px;">验证码有效期为5分钟，请尽快使用。如果您没有进行此操作，请忽略此邮件。</p>
                    <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                    <p style="color: #666; font-size: 14px;">此致<br><strong>Hertz Server Django 团队</strong></p>
                </div>
            </div>
        </body>
        </html>
        '''
        
        text_content = f'''
        {title}
        
        亲爱的 {recipient_name}，
        
        {description}
        
        验证码：{verification_code}
        
        验证码有效期为5分钟，请尽快使用。如果您没有进行此操作，请忽略此邮件。
        
        此致
        Hertz Server Django 团队
        '''
        
        return {
            'subject': subject,
            'html_content': html_content,
            'text_content': text_content
        }