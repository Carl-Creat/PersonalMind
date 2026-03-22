"""
PersonalMind 语音交互模块

支持：
- 语音识别（STT）：语音 -> 文字
- 语音合成（TTS）：文字 -> 语音
- 实时对话模式
"""
import os
import io
import base64
import time
from typing import Optional, Callable, Dict
from dataclasses import dataclass


@dataclass
class VoiceConfig:
    """语音配置"""
    # 语音识别
    stt_engine: str = "openai"  # openai, google, whisper
    stt_language: str = "zh-CN"
    
    # 语音合成
    tts_engine: str = "openai"  # openai, edge, gtts
    tts_voice: str = "alloy"  # alloy, echo, fable, onyx, nova, shimmer
    tts_speed: float = 1.0  # 0.5 - 2.0
    
    # 通用
    audio_format: str = "wav"  # wav, mp3, ogg
    sample_rate: int = 24000


class VoiceInterface:
    """
    语音交互接口
    
    支持多种 TTS/STT 引擎
    """
    
    def __init__(self, config: VoiceConfig = None):
        self.config = config or VoiceConfig()
        self.is_recording = False
    
    def speech_to_text(self, audio_data: bytes) -> str:
        """
        语音识别
        
        Args:
            audio_data: 音频数据（bytes）
        
        Returns:
            识别的文本
        """
        if self.config.stt_engine == "openai":
            return self._openai_stt(audio_data)
        elif self.config.stt_engine == "whisper":
            return self._whisper_stt(audio_data)
        else:
            return self._google_stt(audio_data)
    
    def text_to_speech(self, text: str) -> bytes:
        """
        语音合成
        
        Args:
            text: 要转换的文本
        
        Returns:
            音频数据（bytes）
        """
        if self.config.tts_engine == "openai":
            return self._openai_tts(text)
        elif self.config.tts_engine == "edge":
            return self._edge_tts(text)
        else:
            return self._gtts_tts(text)
    
    def _openai_stt(self, audio_data: bytes) -> str:
        """OpenAI Whisper API"""
        try:
            import openai
            
            # 将 bytes 转为文件-like 对象
            audio_file = io.BytesIO(audio_data)
            audio_file.name = "audio.wav"
            
            client = openai.OpenAI()
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
            
            return response.text
            
        except ImportError:
            return "（请安装 openai 包使用语音识别）"
        except Exception as e:
            return f"（语音识别错误：{str(e)}）"
    
    def _whisper_stt(self, audio_data: bytes) -> str:
        """本地 Whisper 模型"""
        try:
            import whisper
            
            # 保存临时文件
            temp_path = "temp_audio.wav"
            with open(temp_path, "wb") as f:
                f.write(audio_data)
            
            # 加载模型并识别
            model = whisper.load_model("base")
            result = model.transcribe(temp_path)
            
            # 清理
            os.remove(temp_path)
            
            return result["text"]
            
        except ImportError:
            return "（请安装 openai-whisper 包使用本地识别）"
        except Exception as e:
            return f"（识别错误：{str(e)}）"
    
    def _google_stt(self, audio_data: bytes) -> str:
        """Google Speech-to-Text"""
        # 简化实现
        return "（Google STT 需要配置 API Key）"
    
    def _openai_tts(self, text: str) -> bytes:
        """OpenAI TTS API"""
        try:
            import openai
            
            client = openai.OpenAI()
            
            response = client.audio.speech.create(
                model="tts-1",
                voice=self.config.tts_voice,
                input=text,
                speed=self.config.tts_speed
            )
            
            # 返回二进制音频数据
            return response.content
            
        except ImportError:
            return b"（请安装 openai 包使用语音合成）"
        except Exception as e:
            return b"（语音合成错误）"
    
    def _edge_tts(self, text: str) -> bytes:
        """Edge TTS（免费，不需要 API Key）"""
        try:
            import edge_tts
            
            communicate = edge_tts.Communicate(
                text,
                voice=self._get_edge_voice()
            )
            
            audio_data = b""
            async def save(audio):
                nonlocal audio_data
                audio_data += audio
            
            import asyncio
            asyncio.run(communicate.run(save))
            
            return audio_data
            
        except ImportError:
            return b"（请安装 edge-tts 包使用免费语音）"
        except Exception as e:
            return b"（Edge TTS 错误）"
    
    def _gtts_tts(self, text: str) -> bytes:
        """Google TTS（免费但有限制）"""
        try:
            from gtts import gTTS
            
            tts = gTTS(text=text, lang='zh-cn', slow=False)
            
            mp3_data = io.BytesIO()
            tts.write_to_fp(mp3_data)
            mp3_data.seek(0)
            
            return mp3_data.read()
            
        except ImportError:
            return b"（请安装 gTTS 包使用）"
        except Exception as e:
            return b"（TTS 错误）"
    
    def _get_edge_voice(self) -> str:
        """获取 Edge TTS 语音（中文）"""
        voices = {
            "zh-CN": "zh-CN-XiaoxiaoNeural",
            "male": "zh-CN-YunxiNeural",
            "female": "zh-CN-XiaoxiaoNeural"
        }
        return voices.get("zh-CN", "zh-CN-XiaoxiaoNeural")


class VoiceAssistant(VoiceInterface):
    """
    语音助手
    
    对话式语音交互
    """
    
    def __init__(self, text_handler: Callable[[str], str], config: VoiceConfig = None):
        """
        Args:
            text_handler: 文本处理函数（输入文本，返回回复）
            config: 语音配置
        """
        super().__init__(config)
        self.text_handler = text_handler
        self.conversation_history: list = []
    
    def handle_audio_input(self, audio_data: bytes) -> bytes:
        """
        处理语音输入，返回语音回复
        
        Args:
            audio_data: 输入音频
        
        Returns:
            回复音频数据
        """
        # 1. 语音 -> 文字
        user_text = self.speech_to_text(audio_data)
        
        if not user_text or user_text.startswith("（"):
            # 识别失败
            return self.text_to_speech("抱歉，我没有听清楚，请再说一次。")
        
        # 记录对话
        self.conversation_history.append({"role": "user", "content": user_text})
        
        # 2. 文字处理 -> 回复
        reply_text = self.text_handler(user_text)
        
        # 记录回复
        self.conversation_history.append({"role": "assistant", "content": reply_text})
        
        # 3. 文字 -> 语音回复
        reply_audio = self.text_to_speech(reply_text)
        
        return reply_audio
    
    def voice_loop(self, chunk_handler: Callable[[bytes], bytes]):
        """
        实时语音对话循环
        
        Args:
            chunk_handler: 音频块处理器
        """
        print("🎤 语音对话模式启动")
        print("说 '退出' 结束对话\n")
        
        self.is_recording = True
        
        while self.is_recording:
            try:
                # 这里应该接入真实的麦克风输入
                # 简化：模拟
                print("🎙️ 正在聆听...")
                
                # 模拟音频输入（实际应该从麦克风读取）
                # audio_chunk = microphone.read()
                
                # 如果收到 "退出" 指令
                # if "退出" in detected_text:
                #     self.is_recording = False
                #     break
                
                # 处理并回复
                # reply_audio = self.handle_audio_input(audio_chunk)
                # speaker.play(reply_audio)
                
                pass
                
            except KeyboardInterrupt:
                print("\n👋 语音对话结束")
                self.is_recording = False
                break
    
    def stop(self):
        """停止语音对话"""
        self.is_recording = False


def demo():
    """演示"""
    print("=" * 50)
    print("PersonalMind 语音助手演示")
    print("=" * 50)
    
    # 模拟文本处理
    def mock_handler(text: str) -> str:
        return f"你说了：'{text}'。这是一个测试回复。"
    
    # 创建语音助手
    voice = VoiceAssistant(mock_handler)
    
    # 测试语音合成
    print("\n测试语音合成...")
    audio = voice.text_to_speech("你好！我是 PersonalMind 语音助手。你可以对我说话，我会用语音回复你。")
    
    if audio:
        # 保存测试音频
        test_file = "test_voice_output.mp3"
        with open(test_file, "wb") as f:
            f.write(audio)
        print(f"✅ 语音合成成功，已保存到 {test_file}")
    else:
        print("❌ 语音合成失败")
    
    # 测试语音识别（需要真实音频文件）
    print("\n语音识别配置：")
    print(f"  引擎: {voice.config.stt_engine}")
    print(f"  语言: {voice.config.stt_language}")


if __name__ == "__main__":
    demo()
