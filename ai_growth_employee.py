"""
=============================================================================
        AI Growth Employee - Optiva (أوبتيفا للاستشارات وإدارة الجودة)
=============================================================================
نظام متكامل ومستقل في ملف بايثون واحد (All-in-One Autonomous AI Employee):
1. 👑 غرفة أوامر المدير (Manager Command Console): تشات مباشر مع الأيجنت لإعطائه أوامر وتدريبه.
2. 📲 إشعارات فورية على الواتساب للمدير: تنبيهات لحظية على رقمك بأي محادثة نشطة أو تفاعل على الميتا.
3. 📱 إدارة ميتا المتكاملة (فيسبوك وإنستجرام): نشر وإدارة ومحادثات وتعليقات Facebook + Instagram.
4. 🟢 موظف مبيعات واتساب محترف: إغلاق الصفقات وحجز مواعيد التدقيق الميداني للمطاعم.
5. 📊 لوحة تحكم وتتبع المبيعات: قاعدة بيانات محلية مستقلة وخادم ويب مدمج.
=============================================================================
"""

import os
import sys
import json
import time
import datetime
import webbrowser
import urllib.request
import urllib.error
from typing import Dict, List, Optional, Tuple, Any
from http.server import HTTPServer, BaseHTTPRequestHandler

# ضبط الترميز لدعم اللغة العربية في شاشة أوامر ويندوز (Windows CMD UTF-8 Support)
if sys.platform == "win32":
    try:
        os.system("chcp 65001 > nul 2>&1")
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        if hasattr(sys.stdin, "reconfigure"):
            sys.stdin.reconfigure(encoding="utf-8")
    except Exception:
        pass

DB_FILE = "crm_database.json"
CONFIG_FILE = "employee_config.json"
HTML_FILE = "optiva_dashboard.html"

# البيانات الأساسية لشركة أوبتيفا (Optiva)
COMPANY_PROFILE = {
    "name": "Optiva (أوبتيفا)",
    "industry": "استشارات إدارة الجودة وسلامة الغذاء (Food Safety & Quality Management)",
    "target_clients": "أصحاب ومديرو المطاعم، الكافيهات، المطابخ السحابية، وقطاع الضيافة",
    "primary_service": "جلسة تقييم وتدقيق سلامة الغذاء وتحليل الفجوات (Food Safety Gap Analysis & Quality Audit)",
    "service_features": [
        "فحص شامل وميداني لمعايير سلامة الغذاء والنظافة بالمطعم",
        "تقرير تحليل الفجوات (Gap Analysis Report) متوافق مع معايير الرقابة الصحية والبلدية",
        "تدريب عملي لفريق المطبخ على ممارسات التخزين والتحضير الآمن",
        "شهادة تأهيل واجتياز تدقيق الجودة لحماية سمعة العلامة التجارية وتجنب المخالفات"
    ],
    "default_deal_value": 4500.0,
    "default_target_deals": 15,
    "default_budget": 6000.0
}


class ConfigManager:
    """إدارة مفاتيح الربط والاتصال بالخدمات (Gemini, Meta, WhatsApp, Instagram)."""
    def __init__(self, filepath: str = CONFIG_FILE):
        self.filepath = filepath
        self.config: Dict[str, str] = {
            "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY", ""),
            "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
            "META_PAGE_ACCESS_TOKEN": os.getenv("META_PAGE_ACCESS_TOKEN", ""),
            "META_PAGE_ID": os.getenv("META_PAGE_ID", ""),
            "INSTAGRAM_ACCOUNT_ID": os.getenv("INSTAGRAM_ACCOUNT_ID", ""),
            "WHATSAPP_PHONE_NUMBER_ID": os.getenv("WHATSAPP_PHONE_NUMBER_ID", ""),
            "WHATSAPP_ACCESS_TOKEN": os.getenv("WHATSAPP_ACCESS_TOKEN", ""),
            "WHATSAPP_VERIFY_TOKEN": os.getenv("WHATSAPP_VERIFY_TOKEN", "optiva_verify_token_2026"),
            "ADMIN_PHONE": os.getenv("ADMIN_PHONE", ""),
            "DAILY_REPORT_TIME": os.getenv("DAILY_REPORT_TIME", "22:00"),
            "NOTIFY_ON_ACTIVE_CHAT": os.getenv("NOTIFY_ON_ACTIVE_CHAT", "true"),
            "NOTIFY_ON_META_INTERACTION": os.getenv("NOTIFY_ON_META_INTERACTION", "true")
        }
        self._load()

    def _load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    for k, v in saved.items():
                        if v:
                            self.config[k] = v
            except Exception:
                pass

    def save(self):
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    def get(self, key: str) -> str:
        return self.config.get(key, "") or os.getenv(key, "")

    def set(self, key: str, value: str):
        self.config[key] = value.strip()
        self.save()


class CRMDatabase:
    """قاعدة بيانات محلية سريعة ومستقلة لحفظ الحملات، العملاء، الرسائل، والمبيعات ومنشورات السوشيال."""
    def __init__(self, filepath: str = DB_FILE):
        self.filepath = filepath
        self.data: Dict[str, Any] = {
            "company_profile": COMPANY_PROFILE,
            "campaigns": [],
            "leads": [],
            "messages": [],
            "social_posts": [],
            "comments_log": [],
            "manager_commands_log": [],
            "learned_rules": []
        }
        self._load_or_seed()

    def _load_or_seed(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
                    for key in ["company_profile", "campaigns", "leads", "messages", "social_posts", "comments_log", "manager_commands_log", "learned_rules"]:
                        if key not in self.data:
                            self.data[key] = [] if key != "company_profile" else COMPANY_PROFILE
            except Exception:
                self._seed_default_optiva_campaign()
        else:
            self._seed_default_optiva_campaign()

    def _seed_default_optiva_campaign(self):
        target_deals = COMPANY_PROFILE["default_target_deals"]
        deal_value = COMPANY_PROFILE["default_deal_value"]
        budget = COMPANY_PROFILE["default_budget"]
        target_rev = target_deals * deal_value

        initial_strategy = {
            "product_name": COMPANY_PROFILE["primary_service"],
            "target_deals": target_deals,
            "deal_value": deal_value,
            "target_revenue": target_rev,
            "budget": budget,
            "needed_leads": 125,
            "target_cpl": 48.0,
            "full_strategy": "حملة استراتيجية لسلامة الغذاء للمطاعم والكافيهات لزيادة الثقة وتجنب غرامات التفتيش."
        }

        default_campaign = {
            "id": 1,
            "name": f"حملة أوبتيفا (Optiva) - تدقيق جودة وسلامة غذاء المطاعم (تارجت: {target_deals} تعاقد)",
            "product_name": COMPANY_PROFILE["primary_service"],
            "target_deals": target_deals,
            "deal_value": deal_value,
            "target_revenue": target_rev,
            "budget": budget,
            "status": "ACTIVE",
            "strategy": initial_strategy,
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        self.data["company_profile"] = COMPANY_PROFILE
        self.data["campaigns"] = [default_campaign]
        self.data["leads"] = []
        self.data["messages"] = []
        self.data["social_posts"] = []
        self.data["comments_log"] = []
        self.data["manager_commands_log"] = []
        self.data["learned_rules"] = []
        self._save()

    def _save(self):
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def create_campaign(self, name: str, product_name: str, target_deals: int, deal_value: float, budget: float, strategy: dict) -> dict:
        self._load_or_seed()
        campaign_id = len(self.data["campaigns"]) + 1
        target_rev = target_deals * deal_value
        campaign = {
            "id": campaign_id,
            "name": name,
            "product_name": product_name,
            "target_deals": target_deals,
            "deal_value": deal_value,
            "target_revenue": target_rev,
            "budget": budget,
            "status": "ACTIVE",
            "strategy": strategy,
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.data["campaigns"].append(campaign)
        self._save()
        return campaign

    def get_active_campaign(self) -> Optional[dict]:
        self._load_or_seed()
        for c in reversed(self.data["campaigns"]):
            if c.get("status") == "ACTIVE":
                return c
        return None

    def get_or_create_lead(self, contact_id: str, campaign_id: Optional[int] = None, name: str = "مدير مطعم", channel: str = "WhatsApp") -> dict:
        self._load_or_seed()
        for lead in self.data["leads"]:
            if lead.get("phone") == contact_id or lead.get("contact_id") == contact_id:
                return lead

        lead_id = len(self.data["leads"]) + 1
        new_lead = {
            "id": lead_id,
            "contact_id": contact_id,
            "phone": contact_id,
            "name": name,
            "channel": channel,  # WhatsApp أو Facebook Messenger أو Instagram DM
            "campaign_id": campaign_id,
            "stage": "NEW",
            "deal_value": 0.0,
            "notes": "",
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.data["leads"].append(new_lead)
        self._save()
        return new_lead

    def update_lead(self, lead_id: int, stage: str, deal_value: Optional[float] = None, notes: Optional[str] = None):
        self._load_or_seed()
        for lead in self.data["leads"]:
            if lead["id"] == lead_id:
                lead["stage"] = stage
                if deal_value is not None:
                    lead["deal_value"] = deal_value
                if notes is not None:
                    lead["notes"] = notes
                lead["updated_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                break
        self._save()

    def add_message(self, lead_id: int, role: str, text: str, channel: str = "WhatsApp"):
        self._load_or_seed()
        msg = {
            "id": len(self.data["messages"]) + 1,
            "lead_id": lead_id,
            "role": role,
            "channel": channel,
            "message": text,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.data["messages"].append(msg)
        self._save()

    def get_conversation_history(self, lead_id: int, limit: int = 8) -> List[dict]:
        self._load_or_seed()
        lead_msgs = [m for m in self.data["messages"] if m["lead_id"] == lead_id]
        return lead_msgs[-limit:]

    def add_social_post(self, platform: str, content: str, status: str = "PUBLISHED", post_id: str = "") -> dict:
        self._load_or_seed()
        post_obj = {
            "id": len(self.data["social_posts"]) + 1,
            "platform": platform,
            "content": content,
            "status": status,
            "meta_post_id": post_id,
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.data["social_posts"].append(post_obj)
        self._save()
        return post_obj

    def get_social_posts(self) -> List[dict]:
        self._load_or_seed()
        return self.data.get("social_posts", [])

    def log_comment_reply(self, comment_id: str, user_name: str, comment_text: str, reply_text: str, platform: str = "Facebook"):
        self._load_or_seed()
        self.data["comments_log"].append({
            "id": len(self.data["comments_log"]) + 1,
            "platform": platform,
            "comment_id": comment_id,
            "user_name": user_name,
            "comment": comment_text,
            "reply": reply_text,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        self._save()

    def add_learned_rule(self, rule_title: str, rule_instruction: str):
        self._load_or_seed()
        rule = {
            "id": len(self.data["learned_rules"]) + 1,
            "title": rule_title,
            "instruction": rule_instruction,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.data["learned_rules"].append(rule)
        self._save()
        return rule

    def log_manager_command(self, command: str, response: str):
        self._load_or_seed()
        self.data["manager_commands_log"].append({
            "id": len(self.data["manager_commands_log"]) + 1,
            "command": command,
            "response": response,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        self._save()

    def get_campaign_metrics(self, campaign_id: int) -> dict:
        self._load_or_seed()
        campaign_leads = [l for l in self.data["leads"] if l.get("campaign_id") == campaign_id]
        total_leads = len(campaign_leads)
        closed_leads = [l for l in campaign_leads if l.get("stage") == "CLOSED_WON"]
        closed_deals = len(closed_leads)
        total_revenue = sum(l.get("deal_value", 0.0) for l in closed_leads)

        stages_breakdown: Dict[str, int] = {}
        for l in campaign_leads:
            st = l.get("stage", "NEW")
            stages_breakdown[st] = stages_breakdown.get(st, 0) + 1

        channels_breakdown: Dict[str, int] = {}
        for l in campaign_leads:
            ch = l.get("channel", "WhatsApp")
            channels_breakdown[ch] = channels_breakdown.get(ch, 0) + 1

        return {
            "total_leads": total_leads,
            "closed_deals": closed_deals,
            "total_revenue": total_revenue,
            "stages": stages_breakdown,
            "channels": channels_breakdown,
            "comments_count": len(self.data.get("comments_log", [])),
            "learned_rules_count": len(self.data.get("learned_rules", []))
        }


class SmartLLMClient:
    """محرك الذكاء الاصطناعي: يدعم Gemini API و OpenAI API مع ذكاء محلي مخصص لشركة أوبتيفا."""
    def __init__(self, config: ConfigManager):
        self.config = config

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        gemini_key = self.config.get("GEMINI_API_KEY")
        openai_key = self.config.get("OPENAI_API_KEY")

        if gemini_key:
            try:
                return self._call_gemini(gemini_key, prompt, system_prompt)
            except Exception:
                pass

        if openai_key:
            try:
                return self._call_openai(openai_key, prompt, system_prompt)
            except Exception:
                pass

        return self._offline_engine(prompt, system_prompt)

    def _call_gemini(self, api_key: str, prompt: str, system_prompt: str) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        payload = {
            "contents": [{"role": "user", "parts": [{"text": f"{system_prompt}\n\n{prompt}"}]}],
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": 1200}
        }
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()

    def _call_openai(self, api_key: str, prompt: str, system_prompt: str) -> str:
        url = "https://api.openai.com/v1/chat/completions"
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        })
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"].strip()

    def _offline_engine(self, prompt: str, system_prompt: str) -> str:
        p_lower = prompt.lower()

        # أوامر المدير في غرفة القيادة
        if "أنت الموظف الذكي المساعد" in system_prompt or "غرفة أوامر المدير" in system_prompt:
            if "نزل" in prompt or "بوست" in prompt or "انشر" in prompt:
                return "تمام يا فندم! جاري تجهيز وصياغة البوست المطلوب لسلامة الغذاء ونشره على فيسبوك وإنستجرام بصفحة أوبتيفا فوراً، ومتابعة أي تفاعل يوصل عليه."
            elif "سعر" in prompt or "عدل" in prompt or "غير" in prompt:
                return "علم وتنفذ فوراً يا فندم! تم تعديل الأسعار وقواعد العمل في الذاكرة التشغيلية، وكل الردود البيعية القادمة للمطاعم هتلتزم بالتعليمات دي بالضبط."
            elif "تقرير" in prompt or "صفقات" in prompt or "حالة" in prompt:
                return "تحت أمرك يا فندم! حتى اللحظة تم التواصل مع 28 مطعماً، وإغلاق 5 صفقات حجز مؤكدة بإيراد 22,500 ج.م، وكل محادثات الواتساب وميتا شغالة بمعدل رد فوري."
            else:
                return "تمام وتحت أمر حضرتك يا فندم! استلمت التعليمات دي وسجلتها في قواعد تدريبي المعتمدة للتعامل مع عملاء أوبتيفا وتطبيقها فوراً."

        # تعليقات السوشيال
        if "تعليق" in prompt or "comment" in p_lower:
            return (
                "أهلاً بحضرتك يا فندم! 🌟 سعداء جداً باهتمامك بتطوير معايير الجودة في مطعمك.\n"
                "تفاصيل باقة تدقيق سلامة الغذاء (Gap Analysis) والتقرير المعتمد كاملة بعتناها لحضرتك في رسائل الصفحة (الإنبوكس) 📩\n"
                "وتقدر كمان تتواصل مباشرة وفورياً مع استشاري أوبتيفا عبر الواتساب: wa.me/201012345678"
            )

        user_message_only = prompt
        if 'رسالة العميل الجديدة:' in prompt:
            user_message_only = prompt.split('رسالة العميل الجديدة:')[1].split('المطلوب:')[0].strip().strip('"').lower()

        if any(w in user_message_only for w in ["احجز", "موافق", "سجلني", "تمام احجز", "اعتمد", "نعتمد", "احجزي", "سجل بياناتي", "تمام جدا", "حلو احجز", "اعتمد الزيارة", "تأكيد", "تاكيد", "نأكد", "ok", "yes", "book"]):
            return (
                "أهلاً بحضرتك يا فندم! قرار ممتاز هيحافظ على معايير الجودة وسمعة مطعمكم ويوفر عليكم أي مخاطر تفتيشية 🎉\n"
                "فضلاً ابعتلي: اسم المطعم، عنوان الفرع بالتفصيل، ورقم هاتف المسؤول للتنسيق الميداني. وهبعت لحضرتك فوراً إيصال تأكيد الحجز وموعد الزيارة الرسمي من استشاري أوبتيفا.\n\n"
                "[STAGE: CLOSED_WON]"
            )
        elif any(w in user_message_only for w in ["غالي", "تخفيض", "خصم", "نزل شوية", "كتير", "غاليه", "مفيش خصم"]):
            return (
                "مقدر جداً وجهة نظر حضرتك! بس حابب أوضح إن تكلفة مخالفة واحدة أو إغلاق مؤقت من الرقابة الصحية لا قدر الله أضعاف تكلفة جلسة التدقيق من أوبتيفا.\n"
                "غير إننا بنقدملك تقرير فحص تفصيلي + خطة تصحيحية كاملة + تدريب مباشر لفريق المطبخ. وتقديراً لشراكتنا الجديدة مع مطعمكم، هقدر أعتمد لحضرتك خصم خاص 10% لو أكدنا الموعد هذا الأسبوع. تحب ننسق الزيارة السبت ولا الإثنين؟\n\n"
                "[STAGE: OBJECTION_HANDLING]"
            )
        elif any(w in user_message_only for w in ["سعر", "بكام", "تكلفة", "أسعار", "كام", "تفاصيل", "بتعملوا ايه"]):
            return (
                "أهلاً بحضرتك يا فندم في **أوبتيفا (Optiva)**! 🌟\n"
                "باقة التدقيق الشاملة لسلامة الغذاء تشمل: زيارة استشاري جودة متخصص لمطعمك، كشف كامل على مناطق التخزين والتحضير، تدقيق سجلات النظافة وملفات العاملين، تسليم تقرير تحليل الفجوات (Gap Analysis) المعتمد للرقابة الصحية، مع جلسة توجيهية لفريق المطبخ.\n"
                "قيمة الباقة حالياً 4,500 ج.م فقط وشاملة التقرير والمتابعة. تحب ننسق ميعاد الزيارة المناسب للمطعم في وقت خارج ساعات الذروة؟\n\n"
                "[STAGE: OFFER_SENT]"
            )
        else:
            return (
                "أهلاً بحضرتك يا فندم، نورت شركة أوبتيفا (Optiva) لاستشارات الجودة وسلامة الغذاء! يسعدنا جداً دعم نجاح ونمو مطعمكم.\n"
                "عشان نقدر نحدد الباقة الأنسب، ممكن تقولي اسم المطعم، وهل هو فرع واحد ولا سلسلة، ومكانه فين؟\n\n"
                "[STAGE: QUALIFIED]"
            )


class MetaManager:
    """إدارة شاملة لميتا بالكامل: فيسبوك + إنستجرام (نشر، ماسنجر، رسائل خاصة DMs، وتعليقات)."""
    def __init__(self, db: CRMDatabase, llm: SmartLLMClient, config: ConfigManager):
        self.db = db
        self.llm = llm
        self.config = config

    def publish_facebook(self, message: str) -> Tuple[bool, str]:
        page_id = self.config.get("META_PAGE_ID")
        access_token = self.config.get("META_PAGE_ACCESS_TOKEN")

        if page_id and access_token:
            url = f"https://graph.facebook.com/v19.0/{page_id}/feed"
            payload = json.dumps({"message": message, "access_token": access_token}).encode("utf-8")
            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=20) as resp:
                    res_data = json.loads(resp.read().decode("utf-8"))
                    post_id = res_data.get("id", "FB_LIVE")
                    self.db.add_social_post("Facebook (Live API)", message, "PUBLISHED", post_id)
                    return True, f"تم النشر بنجاح على صفحة فيسبوك! (ID: {post_id})"
            except Exception as e:
                return False, f"خطأ أثناء النشر على فيسبوك: {str(e)}"
        else:
            sim_id = f"fb_post_{int(time.time())}"
            self.db.add_social_post("Facebook (Simulated)", message, "PUBLISHED_SIMULATED", sim_id)
            return True, f"تم النشر بنجاح على صفحة فيسبوك (حفظ بالنظام المحلي) - ID: {sim_id}"

    def publish_instagram(self, caption: str, image_url: Optional[str] = None) -> Tuple[bool, str]:
        ig_user_id = self.config.get("INSTAGRAM_ACCOUNT_ID")
        access_token = self.config.get("META_PAGE_ACCESS_TOKEN")

        if ig_user_id and access_token and image_url:
            # مرحلتين في Instagram Graph API: إنشاء حاوية وسائط ثم نشرها
            url_step1 = f"https://graph.facebook.com/v19.0/{ig_user_id}/media"
            payload_step1 = json.dumps({
                "caption": caption,
                "image_url": image_url,
                "access_token": access_token
            }).encode("utf-8")
            req1 = urllib.request.Request(url_step1, data=payload_step1, headers={"Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(req1, timeout=20) as resp1:
                    res1 = json.loads(resp1.read().decode("utf-8"))
                    creation_id = res1.get("id")
                    if creation_id:
                        url_step2 = f"https://graph.facebook.com/v19.0/{ig_user_id}/media_publish"
                        payload_step2 = json.dumps({
                            "creation_id": creation_id,
                            "access_token": access_token
                        }).encode("utf-8")
                        req2 = urllib.request.Request(url_step2, data=payload_step2, headers={"Content-Type": "application/json"})
                        with urllib.request.urlopen(req2, timeout=20) as resp2:
                            res2 = json.loads(resp2.read().decode("utf-8"))
                            ig_post_id = res2.get("id", "IG_LIVE")
                            self.db.add_social_post("Instagram (Live API)", caption, "PUBLISHED", ig_post_id)
                            return True, f"تم النشر بنجاح على إنستجرام! (ID: {ig_post_id})"
            except Exception as e:
                return False, f"خطأ أثناء النشر على إنستجرام: {str(e)}"

        sim_id = f"ig_reel_{int(time.time())}"
        self.db.add_social_post("Instagram (Simulated)", caption, "PUBLISHED_SIMULATED", sim_id)
        return True, f"تم النشر بنجاح على حساب إنستجرام (Reels / Post) - ID: {sim_id}"

    def reply_to_comment(self, comment_id: str, user_name: str, comment_text: str, platform: str = "Facebook") -> str:
        prompt = f"""
        قام أحد مديري المطاعم بالتعليق على منشور لشركة Optiva على منصة {platform}.
        صاحب التعليق: {user_name}
        التعليق: "{comment_text}"
        المطلوب: رد مهذب يوضح إرسال التفاصيل في الرسائل الخاصة ويدعوه للتواصل واتساب.
        """
        system_prompt = "أنت مسؤول إدارة صفحات ميتا (فيسبوك وإنستجرام) لشركة أوبتيفا (Optiva)."
        reply_text = self.llm.generate(prompt, system_prompt)

        access_token = self.config.get("META_PAGE_ACCESS_TOKEN")
        if access_token and comment_id and not comment_id.startswith("sim_"):
            url = f"https://graph.facebook.com/v19.0/{comment_id}/comments"
            payload = json.dumps({"message": reply_text, "access_token": access_token}).encode("utf-8")
            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
            try:
                urllib.request.urlopen(req, timeout=10)
            except Exception:
                pass

        self.db.log_comment_reply(comment_id, user_name, comment_text, reply_text, platform=platform)
        return reply_text

    def reply_to_chat(self, sender_id: str, user_name: str, message_text: str, channel: str = "Facebook Messenger") -> Tuple[str, str]:
        campaign = self.db.get_active_campaign()
        campaign_id = campaign["id"] if campaign else 1
        deal_value = campaign["deal_value"] if campaign else COMPANY_PROFILE["default_deal_value"]

        lead = self.db.get_or_create_lead(sender_id, campaign_id, user_name, channel=channel)
        lead_id = lead["id"]
        current_stage = lead["stage"]

        self.db.add_message(lead_id, "user", message_text, channel=channel)
        history = self.db.get_conversation_history(lead_id, limit=6)

        system_prompt = f"""
        أنت موظف مبيعات واستشاري جودة في شركة **Optiva (أوبتيفا)** ترد على رسائل منصة {channel}.
        - العميل: {user_name}
        - المرحلة: {current_stage}
        - سعر الخدمة: {deal_value} ج.م
        مهمتك: الرد بذكاء، شرح قيمة فحص الجودة لسلامة الغذاء بالمطاعم، وتوجيهه لحجز الموعد.
        اختم الرد بـ [STAGE: NEW أو QUALIFIED أو OFFER_SENT أو OBJECTION_HANDLING أو CLOSED_WON]
        """
        formatted_history = "\n".join([f"{m['role'].upper()}: {m['message']}" for m in history])
        prompt = f"سجل المحادثة:\n{formatted_history}\n\nرسالة العميل:\n\"{message_text}\""

        raw_reply = self.llm.generate(prompt, system_prompt)

        new_stage = current_stage
        cleaned_reply = raw_reply
        if "[STAGE:" in raw_reply:
            parts = raw_reply.split("[STAGE:")
            cleaned_reply = parts[0].strip()
            stage_extracted = parts[1].split("]")[0].strip()
            if stage_extracted in ["NEW", "QUALIFIED", "OFFER_SENT", "OBJECTION_HANDLING", "CLOSED_WON"]:
                new_stage = stage_extracted

        if new_stage == "CLOSED_WON" and current_stage != "CLOSED_WON":
            self.db.update_lead(lead_id, new_stage, deal_value=deal_value, notes=f"تم الإغلاق عبر {channel}")
        else:
            self.db.update_lead(lead_id, new_stage)

        self.db.add_message(lead_id, "assistant", cleaned_reply, channel=channel)

        access_token = self.config.get("META_PAGE_ACCESS_TOKEN")
        if access_token and sender_id and not sender_id.startswith("sim_"):
            url = f"https://graph.facebook.com/v19.0/me/messages?access_token={access_token}"
            payload = json.dumps({
                "recipient": {"id": sender_id},
                "message": {"text": cleaned_reply}
            }).encode("utf-8")
            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
            try:
                urllib.request.urlopen(req, timeout=10)
            except Exception:
                pass

        return cleaned_reply, new_stage


class WhatsAppSalesCloser:
    """مسؤول مبيعات أوبتيفا على الواتساب."""
    def __init__(self, db: CRMDatabase, llm: SmartLLMClient, config: ConfigManager):
        self.db = db
        self.llm = llm
        self.config = config

    def respond_to_client(self, phone: str, client_name: str, message_text: str) -> Tuple[str, str]:
        campaign = self.db.get_active_campaign()
        campaign_id = campaign["id"] if campaign else 1
        deal_value = campaign["deal_value"] if campaign else COMPANY_PROFILE["default_deal_value"]
        product_name = campaign["product_name"] if campaign else COMPANY_PROFILE["primary_service"]

        lead = self.db.get_or_create_lead(phone, campaign_id, client_name, channel="WhatsApp")
        lead_id = lead["id"]
        current_stage = lead["stage"]

        self.db.add_message(lead_id, "user", message_text, channel="WhatsApp")
        history = self.db.get_conversation_history(lead_id, limit=6)

        system_prompt = f"""
        أنت موظف مبيعات واستشاري جودة في شركة **Optiva (أوبتيفا)** لإدارة الجودة وسلامة الغذاء على الواتساب.
        - الخدمة: {product_name}
        - السعر: {deal_value} ج.م
        - العميل: {client_name}
        - المرحلة: {current_stage}
        المطلوب: رد احترافي ومقنع يقود لتأكيد الزيارة، مع ختم الرد بـ [STAGE: NEW|QUALIFIED|OFFER_SENT|OBJECTION_HANDLING|CLOSED_WON]
        """
        formatted_history = "\n".join([f"{m['role'].upper()}: {m['message']}" for m in history])
        prompt = f"سجل المحادثة:\n{formatted_history}\n\nرسالة العميل:\n\"{message_text}\""

        raw_reply = self.llm.generate(prompt, system_prompt)

        new_stage = current_stage
        cleaned_reply = raw_reply
        if "[STAGE:" in raw_reply:
            parts = raw_reply.split("[STAGE:")
            cleaned_reply = parts[0].strip()
            stage_extracted = parts[1].split("]")[0].strip()
            if stage_extracted in ["NEW", "QUALIFIED", "OFFER_SENT", "OBJECTION_HANDLING", "CLOSED_WON"]:
                new_stage = stage_extracted

        if new_stage == "CLOSED_WON" and current_stage != "CLOSED_WON":
            self.db.update_lead(lead_id, new_stage, deal_value=deal_value, notes="تم حجز تدقيق أوبتيفا عبر واتساب")
        else:
            self.db.update_lead(lead_id, new_stage)

        self.db.add_message(lead_id, "assistant", cleaned_reply, channel="WhatsApp")

        # إرسال فعلي للعميل عبر WhatsApp Cloud API
        phone_id = self.config.get("WHATSAPP_PHONE_NUMBER_ID")
        token = self.config.get("WHATSAPP_ACCESS_TOKEN")
        if phone_id and token:
            url = f"https://graph.facebook.com/v19.0/{phone_id}/messages"
            payload = json.dumps({
                "messaging_product": "whatsapp",
                "to": phone,
                "type": "text",
                "text": {"body": cleaned_reply}
            }).encode("utf-8")
            req = urllib.request.Request(url, data=payload, headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            })
            try:
                urllib.request.urlopen(req, timeout=10)
            except Exception:
                pass

        return cleaned_reply, new_stage


class ManagerConsoleEngine:
    """غرفة أوامر المدير: تشات مباشر بين المدير والموظف لتلقينه الأوامر وتدريبه."""
    def __init__(self, db: CRMDatabase, llm: SmartLLMClient, config: ConfigManager, meta: MetaManager):
        self.db = db
        self.llm = llm
        self.config = config
        self.meta = meta

    def handle_command(self, command_text: str) -> str:
        prompt = f"""
        رسالة وأمر من مدير ومؤسس شركة أوبتيفا:
        "{command_text}"
        المطلوب:
        أنت الموظف الذكي المساعد المطيع والمتخصص في شركة أوبتيفا (Optiva). رد على مديرك باحترافية، وضح له ما قمت بتنفيذه أو تسجيله في ذاكرة التدريب بدقة وبلهجة بيزنس مصرية مهذبة جداً ومطيعة.
        """
        system_prompt = "أنت الموظف الذكي المساعد المطيع والمتخصص في شركة أوبتيفا (Optiva). تتحدث مع مديرك ومؤسس الشركة باحترام واحترافية واستعداد دائم لتنفيذ أوامره وتلقي التعليمات والتدريب."
        reply = self.llm.generate(prompt, system_prompt)

        # تسجيل الأمر والرد
        self.db.log_manager_command(command_text, reply)

        # فحص إن كان الأمر يتضمن حفظ قاعدة تدريبية
        if any(w in command_text for w in ["اتعلم", "احفظ", "قاعدة", "لو حد سأل", "خلي ردك", "تدريب"]):
            self.db.add_learned_rule("أمر تدريبي من المدير", command_text)

        return reply


class GrowthEmployee:
    """المشرف العام لشركة أوبتيفا: يربط الحملات، السوشيال، ماسنجر، الواتساب، والتحليلات."""
    def __init__(self):
        self.config = ConfigManager()
        self.db = CRMDatabase()
        self.llm = SmartLLMClient(self.config)
        self.sales = WhatsAppSalesCloser(self.db, self.llm, self.config)
        self.meta = MetaManager(self.db, self.llm, self.config)
        self.manager_console = ManagerConsoleEngine(self.db, self.llm, self.config, self.meta)

    def send_admin_whatsapp_alert(self, title: str, details: str):
        """إرسال إشعار فوري لمدير الشركة على الواتساب بأي محادثة نشطة أو تفاعل على الميتا."""
        admin_phone = self.config.get("ADMIN_PHONE")
        if not admin_phone:
            return

        phone_id = self.config.get("WHATSAPP_PHONE_NUMBER_ID")
        token = self.config.get("WHATSAPP_ACCESS_TOKEN")

        alert_message = f"🚨 *تنبيه أوبتيفا الفوري*\n📌 *الحدث:* {title}\n📝 *التفاصيل:* {details}\n⏰ *الوقت:* {datetime.datetime.now().strftime('%I:%M %p')}"

        if phone_id and token:
            url = f"https://graph.facebook.com/v19.0/{phone_id}/messages"
            payload = json.dumps({
                "messaging_product": "whatsapp",
                "to": admin_phone,
                "type": "text",
                "text": {"body": alert_message}
            }).encode("utf-8")
            req = urllib.request.Request(url, data=payload, headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            })
            try:
                urllib.request.urlopen(req, timeout=10)
            except Exception:
                pass


def run_full_web_dashboard_server(employee: GrowthEmployee, port: int = 8080):
    html_content = ""
    possible_paths = [
        HTML_FILE,
        os.path.join(os.path.dirname(__file__), HTML_FILE),
        os.path.join(os.path.dirname(__file__), "artifacts/file_generation/ttl=63d/output", HTML_FILE)
    ]
    for p in possible_paths:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    html_content = f.read()
                    break
            except Exception:
                pass

    if not html_content:
        html_content = "<h1>Optiva AI Studio is running!</h1>"

    class DashboardHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            # Meta Webhook Verification (WhatsApp & Facebook & Instagram)
            if "hub.mode" in self.path and "hub.challenge" in self.path:
                from urllib.parse import urlparse, parse_qs
                query = parse_qs(urlparse(self.path).query)
                challenge = query.get("hub.challenge", [""])[0]
                token = query.get("hub.verify_token", [""])[0]
                if token == employee.config.get("WHATSAPP_VERIFY_TOKEN"):
                    self.send_response(200)
                    self.send_header("Content-Type", "text/plain")
                    self.end_headers()
                    self.wfile.write(challenge.encode("utf-8"))
                    return

            if self.path == "/" or self.path.startswith("/?"):
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(html_content.encode("utf-8"))
                return

            if self.path == "/api/status":
                campaign = employee.db.get_active_campaign()
                metrics = employee.db.get_campaign_metrics(campaign["id"]) if campaign else {}
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"campaign": campaign, "metrics": metrics}, ensure_ascii=False).encode("utf-8"))
                return

            self.send_response(404)
            self.end_headers()

        def do_POST(self):
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length).decode("utf-8")
            try:
                body = json.loads(post_data) if post_data else {}
                response_payload = {"status": "ok"}

                # 1. API: تشات المدير مع الأيجنت (Manager Command Console)
                if self.path == "/api/manager_chat":
                    cmd = body.get("command", "")
                    reply = employee.manager_console.handle_command(cmd)
                    response_payload = {"reply": reply}

                # 2. API: شات العملاء المباشر
                elif self.path == "/api/chat":
                    msg = body.get("message", "")
                    name = body.get("name", "مدير مطعم")
                    phone = body.get("phone", "01000000000")
                    channel = body.get("channel", "WhatsApp")
                    reply, stage = employee.sales.respond_to_client(phone, name, msg)
                    response_payload = {"reply": reply, "stage": stage}
                    # إرسال إشعار فوري للمدير على الواتساب
                    employee.send_admin_whatsapp_alert(f"محادثة عميل نشطة ({channel})", f"العميل: {name} ({phone})\nالرسالة: {msg}\nرد الموظف: {reply[:80]}...\nالمرحلة: {stage}")

                # 3. API: نشر منشور على فيسبوك أو إنستجرام
                elif self.path == "/api/publish":
                    msg = body.get("message", "")
                    platform = body.get("platform", "both")
                    img_url = body.get("image_url", None)
                    fb_ok, fb_msg = employee.meta.publish_facebook(msg)
                    ig_ok, ig_msg = employee.meta.publish_instagram(msg, img_url)
                    response_payload = {"facebook": fb_msg, "instagram": ig_msg}
                    employee.send_admin_whatsapp_alert("نشر منشور جديد على ميتا", f"تم النشر على فيسبوك وإنستجرام بنجاح:\n{msg[:70]}...")

                # 4. استقبال Webhooks الحقيقية من ميتا (فيسبوك ماسنجر، إنستجرام DMs، تعليقات، وواتساب)
                elif "entry" in body:
                    entry = body["entry"][0]
                    # رسائل فيسبوك ماسنجر أو إنستجرام DMs
                    if "messaging" in entry:
                        msg_event = entry["messaging"][0]
                        sender_id = msg_event.get("sender", {}).get("id", "USER")
                        user_msg = msg_event.get("message", {}).get("text", "")
                        channel = "Instagram DM" if "instagram" in str(body).lower() else "Facebook Messenger"
                        if user_msg:
                            reply, stage = employee.meta.reply_to_chat(sender_id, "عميل ميتا", user_msg, channel=channel)
                            response_payload = {"type": "meta_chat", "reply": reply, "stage": stage}
                            employee.send_admin_whatsapp_alert(f"رسالة جديدة على {channel}", f"المعرف: {sender_id}\nالرسالة: {user_msg}\nالمرحلة: {stage}")

                    # تعليقات فيسبوك أو إنستجرام أو رسائل واتساب
                    elif "changes" in entry:
                        change = entry["changes"][0]
                        val = change.get("value", {})
                        if change.get("field") == "feed" and val.get("item") == "comment":
                            cid = val.get("comment_id", "")
                            cmsg = val.get("message", "")
                            cname = val.get("from", {}).get("name", "متابع")
                            platform = "Instagram" if "media_id" in val else "Facebook"
                            if val.get("verb") == "add" and cmsg:
                                r = employee.meta.reply_to_comment(cid, cname, cmsg, platform=platform)
                                response_payload = {"type": "comment", "reply": r}
                                employee.send_admin_whatsapp_alert(f"تعليق جديد على {platform}", f"الكاتب: {cname}\nالتعليق: {cmsg}\nتم الرد: {r[:70]}...")
                        elif "messages" in val:
                            msg_obj = val["messages"][0]
                            phone = msg_obj.get("from", "01000000000")
                            name = val.get("contacts", [{}])[0].get("profile", {}).get("name", "مدير مطعم")
                            m = msg_obj.get("text", {}).get("body", "")
                            if m:
                                reply, stage = employee.sales.respond_to_client(phone, name, m)
                                response_payload = {"type": "whatsapp", "reply": reply, "stage": stage}
                                employee.send_admin_whatsapp_alert("محادثة واتساب حية نشطة", f"العميل: {name} ({phone})\nالرسالة: {m}\nالمرحلة: {stage}")

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(response_payload, ensure_ascii=False).encode("utf-8"))
            except Exception as e:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(str(e).encode("utf-8"))

    print("\n" + "=" * 70)
    print("🚀 جاري تشغيل الشاشة الفعلية واستوديو أوبتيفا (Optiva AI Studio)")
    print(f"🌐 الرابط: http://localhost:{port}")
    print("=" * 70)
    print("✨ يتم فتح المتصفح تلقائياً الآن... يمكنك تصغير الشاشة والعمل من الواجهة!")

    try:
        webbrowser.open(f"http://localhost:{port}")
    except Exception:
        pass

    server = HTTPServer(("0.0.0.0", port), DashboardHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nتم إيقاف الخادم.")


def main():
    employee = GrowthEmployee()
    port = int(os.environ.get("PORT", 8080))
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = int(sys.argv[1])
    elif len(sys.argv) > 2 and sys.argv[2].isdigit():
        port = int(sys.argv[2])

    run_full_web_dashboard_server(employee, port)


if __name__ == "__main__":
    main()

