from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django import forms
from hertz_studio_django_captcha.captcha_generator import HertzCaptchaGenerator
import json
from django.conf import settings
import random
import string

class HertzCaptchaForm(forms.Form):
    """Hertz验证码表单"""
    captcha_input = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={
            'placeholder': '请输入验证码',
            'class': 'form-control',
            'autocomplete': 'off'
        }),
        label='验证码'
    )
    captcha_id = forms.CharField(widget=forms.HiddenInput(), required=False)

def captcha_demo(request):
    """
    验证码演示页面
    展示多种验证码功能的使用方法
    """
    # 获取请求的验证码类型
    captcha_type = request.GET.get('type', 'random_char')
    
    # 初始化验证码生成器
    captcha_generator = HertzCaptchaGenerator()
    
    if request.method == 'POST':
        # 检查是否是Ajax请求
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            try:
                data = json.loads(request.body)
                action = data.get('action')
                
                if action == 'refresh':
                    # 刷新验证码
                    captcha_data = captcha_generator.generate_captcha()
                    return JsonResponse({
                        'success': True,
                        'data': captcha_data
                    })
                elif action == 'verify':
                    # 验证验证码
                    captcha_id = data.get('captcha_id', '')
                    user_input = data.get('user_input', '')
                    
                    is_valid = captcha_generator.verify_captcha(captcha_id, user_input)
                    
                    if is_valid:
                        return JsonResponse({
                            'success': True,
                            'valid': True,
                            'message': f'验证成功！验证码类型: {captcha_type}'
                        })
                    else:
                        return JsonResponse({
                            'success': True,
                            'valid': False,
                            'message': '验证码错误，请重新输入'
                        })
            except json.JSONDecodeError:
                return JsonResponse({
                    'success': False,
                    'error': '请求数据格式错误'
                })
        else:
            # 普通表单提交处理
            form = HertzCaptchaForm(request.POST)
            username = request.POST.get('username', '')
            captcha_id = request.POST.get('captcha_id', '')
            captcha_input = request.POST.get('captcha_input', '')
            
            # 验证验证码
            is_valid = captcha_generator.verify_captcha(captcha_id, captcha_input)
            
            if is_valid and username:
                # 生成新的验证码用于显示
                initial_captcha = captcha_generator.generate_captcha()
                return render(request, 'captcha_demo.html', {
                    'form': HertzCaptchaForm(),
                    'success_message': f'验证成功！用户名: {username}，验证码类型: {captcha_type}',
                    'captcha_unavailable': False,
                    'current_type': captcha_type,
                    'initial_captcha': initial_captcha,
                    'captcha_types': {
                        'random_char': '随机字符验证码',
                        'math': '数学运算验证码', 
                        'word': '单词验证码'
                    }
                })
    
    # GET请求或表单验证失败时，生成初始验证码
    form = HertzCaptchaForm()
    initial_captcha = captcha_generator.generate_captcha()
    
    return render(request, 'captcha_demo.html', {
        'form': form,
        'captcha_unavailable': False,
        'current_type': captcha_type,
        'initial_captcha': initial_captcha,
        'captcha_types': {
            'random_char': '随机字符验证码',
            'math': '数学运算验证码', 
            'word': '单词验证码'
        }
    })

def websocket_demo(request):
    """WebSocket演示页面"""
    return render(request, 'websocket_demo.html')

def websocket_test(request):
    """
    WebSocket简单测试页面
    """
    return render(request, 'websocket_test.html')

# 测试热重启功能 - 添加注释触发文件变化

def email_demo(request):
    """邮件系统演示页面"""
    if request.method == 'GET':
        return render(request, 'email_demo.html')
    
    elif request.method == 'POST':
        try:
            # 获取表单数据
            email_type = request.POST.get('email_type', 'welcome')
            recipient_email = request.POST.get('recipient_email')
            recipient_name = request.POST.get('recipient_name', '用户')
            custom_subject = request.POST.get('subject', '')
            custom_message = request.POST.get('message', '')
            
            if not recipient_email:
                return JsonResponse({
                    'success': False,
                    'message': '请输入收件人邮箱地址'
                })
            
            # 根据邮件类型生成内容
            email_content = generate_email_content(email_type, recipient_name, custom_subject, custom_message)
            
            # 发送邮件
            success = send_demo_email(
                recipient_email=recipient_email,
                subject=email_content['subject'],
                html_content=email_content['html_content'],
                text_content=email_content['text_content']
            )
            
            if success:
                return JsonResponse({
                    'success': True,
                    'message': f'邮件已成功发送到 {recipient_email}'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': '邮件发送失败，请检查邮件配置'
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'发送失败：{str(e)}'
            })

def generate_email_content(email_type, recipient_name, custom_subject='', custom_message=''):
    """根据邮件类型生成邮件内容"""
    
    email_templates = {
        'welcome': {
            'subject': '🎉 欢迎加入 Hertz Server Django！',
            'html_template': f'''
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                        <h1 style="margin: 0; font-size: 28px;">🎉 欢迎加入我们！</h1>
                    </div>
                    <div style="background: white; padding: 30px; border: 1px solid #e1e5e9; border-radius: 0 0 10px 10px;">
                        <p style="font-size: 16px;">亲爱的 <strong>{recipient_name}</strong>，</p>
                        <p>欢迎您注册成为我们的用户！我们很高兴您能加入我们的大家庭。</p>
                        <p>在这里，您可以享受到：</p>
                        <ul style="color: #666;">
                            <li>🔐 安全的验证码系统</li>
                            <li>🌐 实时WebSocket通信</li>
                            <li>📧 完善的邮件服务</li>
                            <li>📚 详细的API文档</li>
                        </ul>
                        <p>如果您有任何问题，请随时联系我们。</p>
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="http://127.0.0.1:8000/" style="background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">开始使用</a>
                        </div>
                        <p>祝您使用愉快！</p>
                        <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                        <p style="color: #666; font-size: 14px;">此致<br><strong>Hertz Server Django 团队</strong></p>
                    </div>
                </div>
            </body>
            </html>
            '''
        },
        'notification': {
            'subject': '🔔 系统通知 - Hertz Server Django',
            'html_template': f'''
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background: #007bff; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0;">
                        <h1 style="margin: 0; font-size: 24px;">🔔 系统通知</h1>
                    </div>
                    <div style="background: white; padding: 30px; border: 1px solid #e1e5e9; border-radius: 0 0 10px 10px;">
                        <p style="font-size: 16px;">亲爱的 <strong>{recipient_name}</strong>，</p>
                        <p>您有一条新的系统通知：</p>
                        <div style="background: #f8f9fa; padding: 20px; border-left: 4px solid #007bff; margin: 20px 0;">
                            <p style="margin: 0; font-weight: 500;">您的账户设置已更新，如果这不是您的操作，请立即联系我们。</p>
                        </div>
                        <p>系统会持续为您提供安全保障，如有疑问请联系客服。</p>
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="http://127.0.0.1:8000/" style="background: #007bff; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">查看详情</a>
                        </div>
                        <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                        <p style="color: #666; font-size: 14px;">此致<br><strong>Hertz Server Django 团队</strong></p>
                    </div>
                </div>
            </body>
            </html>
            '''
        },
        'verification': {
            'subject': '🔐 邮箱验证 - Hertz Server Django',
            'html_template': f'''
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background: #28a745; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0;">
                        <h1 style="margin: 0; font-size: 24px;">🔐 邮箱验证</h1>
                    </div>
                    <div style="background: white; padding: 30px; border: 1px solid #e1e5e9; border-radius: 0 0 10px 10px;">
                        <p style="font-size: 16px;">亲爱的 <strong>{recipient_name}</strong>，</p>
                        <p>感谢您注册 Hertz Server Django！请点击下面的按钮验证您的邮箱地址：</p>
                        <div style="text-align: center; margin: 40px 0;">
                            <a href="http://127.0.0.1:8000/verify?token=demo_token" style="background: #28a745; color: white; padding: 15px 40px; text-decoration: none; border-radius: 5px; display: inline-block; font-size: 16px; font-weight: 500;">验证邮箱地址</a>
                        </div>
                        <p style="color: #666; font-size: 14px;">如果按钮无法点击，请复制以下链接到浏览器：<br>
                        <code style="background: #f8f9fa; padding: 5px; border-radius: 3px;">http://127.0.0.1:8000/verify?token=demo_token</code></p>
                        <p style="color: #666;">如果您没有注册账户，请忽略此邮件。此验证链接将在24小时后失效。</p>
                        <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                        <p style="color: #666; font-size: 14px;">此致<br><strong>Hertz Server Django 团队</strong></p>
                    </div>
                </div>
            </body>
            </html>
            '''
        },
        'custom': {
            'subject': custom_subject or '自定义邮件 - Hertz Server Django',
            'html_template': f'''
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0;">
                        <h1 style="margin: 0; font-size: 24px;">{custom_subject or '自定义邮件'}</h1>
                    </div>
                    <div style="background: white; padding: 30px; border: 1px solid #e1e5e9; border-radius: 0 0 10px 10px;">
                        <p style="font-size: 16px;">亲爱的 <strong>{recipient_name}</strong>，</p>
                        <div style="margin: 20px 0; font-size: 16px;">
                            {custom_message.replace(chr(10), '<br>') if custom_message else '这是一封自定义邮件。'}
                        </div>
                        <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                        <p style="color: #666; font-size: 14px;">此致<br><strong>Hertz Server Django 团队</strong></p>
                    </div>
                </div>
            </body>
            </html>
            '''
        }
    }
    
    template = email_templates.get(email_type, email_templates['welcome'])
    html_content = template['html_template']
    text_content = strip_tags(html_content)
    
    return {
        'subject': template['subject'],
        'html_content': html_content,
        'text_content': text_content
    }

def send_demo_email(recipient_email, subject, html_content, text_content):
    """发送演示邮件"""
    try:
        # 检查邮件配置
        if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
            print("邮件配置不完整，使用控制台输出模式")
            print(f"收件人: {recipient_email}")
            print(f"主题: {subject}")
            print(f"内容: {text_content[:200]}...")
            return True
        
        # 创建邮件
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient_email]
        )
        
        # 添加HTML内容
        email.attach_alternative(html_content, "text/html")
        
        # 发送邮件
        email.send()
        return True
        
    except Exception as e:
        print(f"邮件发送失败: {str(e)}")
        return False
