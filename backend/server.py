from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Models
class Topic(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    completed: bool = False
    week: Optional[str] = None

class Subject(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    topics: List[Topic] = []

class TopicUpdate(BaseModel):
    completed: bool

# Initialize curriculum data
CURRICULUM_DATA = {
    "Türkçe": [
        "Türkçe Ses Bilgisi", "Sözcükte Yapı", "İsim (Ad)", "Sıfat", "Zamir", 
        "Tamlamalar", "Zarf", "Edat-Bağlaç-Ünlem", "Fiil-Fiil Çekimi", "Fiil-Ek Fiil",
        "Fiil-Fiilde Yapı", "Fiil-Fiilimsi", "Fiil-Fiilde Çatı", "Cümlenin Öğeleri",
        "Cümle Türleri", "Yazım Kuralları", "Noktalama İşaretleri", "Anlatım Bozuklukları",
        "Sözcükte Anlam", "Cümlede Anlam", "Paragraf", "Batı Edebiyatı Akımları",
        "Şiir Bilgisi-İmge-Ölçü-Uyak", "Şiir Bilgisi-Şiir Türleri", "Şiir Bilgisi-Söz Sanatları",
        "İslamiyet Öncesi Türk Edebiyatı", "Geçiş Dönemi", "Anonim Halk Edebiyatı",
        "Aşık Tarzı Halk Edebiyatı", "Tekke-Tasavvuf Halk Edebiyatı", "Divan Edebiyatı",
        "Tanzimat Edebiyatı", "Servet-i Fünun Edebiyatı", "Fecri Ati Edebiyatı",
        "Milli Edebiyat-Şiir", "Milli Edebiyat-Roman-Hikaye", "Milli Edebiyat-Tiyatro",
        "Milli Edebiyat-Öğretici Metinler", "Cumhuriyet Dönemi-Şiir", 
        "Cumhuriyet Dönemi-Roman-Hikaye", "Cumhuriyet Dönemi-Tiyatro",
        "Cumhuriyet Dönemi-Öğretici Metinler", "Metinlerin Sınıflandırılması"
    ],
    "Fizik": [
        "Fizik Bilimine Giriş", "Madde ve Özellikleri", "Basınç", "Sıvıların Kaldırma Kuvveti",
        "Isı ve Sıcaklık", "Genleşme", "Elektrostatik", "Elektrik Akımı", "Ohm Yasası",
        "Dirençlerin ve Üreteçlerin Bağlanması", "Lambalar", "Mıknatıs ve Manyetik Alan",
        "Aydınlanma", "Gölge", "Düzlem Aynalar", "Küresel Aynalar", "Kırılma", "Renk",
        "Mercekler", "Dalgalar Temel Kavramlar", "Yay Dalgaları", "Su Dalgaları", "Ses Dalgası",
        "Vektör Kuvvet", "Tork", "Denge", "Kütle Merkezi", "Basit Makineler", "Doğrusal Hareket",
        "Bağıl Hareket", "Newton Hareket Yasaları", "İş Enerji", "Atışlar", "İtme Momentum",
        "Çembersel Hareket", "Açısal Momentum", "Kütle Çekimi ve Kepler Yasaları",
        "Basit Harmonik Hareket", "Elektriksel Kuvvet ve Elektrik Alan", "Elektrik Potansiyel",
        "Yüklü Levhalar", "Sığaçlar", "Akımın Manyetik Etkisi", "Manyetik Kuvvet",
        "Manyetik İndüksiyon", "Alternatif Akım", "Transformatörler", "Dalga Mekaniği",
        "Doppler Olayı ve Elektromanyetik Dalgalar", "Atom Kavramının Tarihsel Gelişimi",
        "Büyük Patlama ve Evrenin Oluşumu", "Radyoaktivite", "Özel Görelilik", "Kara Cisim Şımasi",
        "Fotoelektrik Olay", "Compton ve De Brogile", "Görüntüleme Teknolojileri",
        "Süper İletkenlik Nanoteknoloji Lazer"
    ],
    "Kimya": [
        "Kimya Bilimi", "Atom ve Yapı Taşları", "Modern Atom Teorisi", "Periyodik Sistem",
        "Kimyasal Türler Arası Etkileşim", "Temel Yasa", "Mol Kavramı", "Tepkime Türleri (Asit Baz Dahil)",
        "Kimyasal Hesaplar", "Kimyasal Hesaplamalar", "Elektrokimya", "Maddenin Halleri",
        "Doğa ve Kimya", "Gazlar", "Karbon Kimyasına Giriş", "Alkanlar", "Alkenler", "Alkinler",
        "Aromatik Bileşikler", "Alkol", "Eter", "Aldehit", "Keton", "Karboksilik Asit", "Esterler",
        "Karışımlar", "Sıvı Çözeltiler", "Kimya Heryerde", "Tepkimelerde Enerji", "Tepkimelerde Hız",
        "Denge", "Asit Baz Dengesi", "Çözünürlük Dengesi"
    ],
    "Biyoloji": [
        "Canlıların Ortak Özellikleri", "İnorganik Bileşikler", "Organik Bileşikler", "Nükleik Asitler",
        "Genden Proteine", "Hücrenin Yapısı", "Hücre Organelleri", "Hücre Zarında Madde Taşınması",
        "Canlıların Sınıflandırılması", "Canlı Alemleri", "Ekosistem Ekolojisi", 
        "Komünite ve Populasyon Ekolojisi", "Hücresel Solunum", "Fotosentez ve Kemosentez",
        "Hücre Bölünmeleri", "Eşeyli ve Eşeysiz Üreme", "Kalıtım", "Biyoteknoloji ve Genetik Mühendisliği",
        "Sinir Sistemi", "Endokrin Sistemi", "Duyu Organları", "Destek ve Hareket Sistemi",
        "Sindirim Sistemi", "Dolaşım Sistemi", "Bağışıklık Sistemi", "Solunum Sistemi",
        "Üriner Sistem", "Üreme Sistemi", "Bitki Biyolojisi - Bitkisel Yapılar",
        "Bitkilerde Taşıma", "Bitki Biyolojisi - Beslenme", "Bitki Biyolojisi - Büyüme",
        "Bitki Biyolojisi - Hareket", "Bitkilerde Büyüme"
    ],
    "Matematik": [
        "Trigonometri", "Logaritma", "Fonksiyonlar", "Polinom Fonksiyonlar", "Üstel ve Logaritmik Fonksiyonlar",
        "Trigonometrik Fonksiyonlar", "Fonksiyonlarda Limit", "Türev", "Türev Uygulamaları",
        "İntegral", "İntegral Uygulamaları", "Diziler", "Seriler", "Matematik Tümevarımı",
        "Binom Açılımı", "Olasılık", "İstatistik", "Permütasyon", "Kombinasyon", "Analitik Geometri",
        "Doğru Denklemi", "Çember Denklemi", "Parabol", "Elips", "Hiperbol", "Matrisler",
        "Determinant", "Lineer Denklem Sistemleri"
    ]
}

@api_router.get("/")
async def root():
    return {"message": "Müfredat To-Do List API"}

@api_router.get("/subjects", response_model=List[dict])
async def get_subjects():
    """Get all subjects with topic count and completion stats"""
    subjects = []
    for name in CURRICULUM_DATA.keys():
        # Get or create subject in database
        subject_doc = await db.subjects.find_one({"name": name})
        if not subject_doc:
            # Initialize subject with topics
            topics_data = [{"id": str(uuid.uuid4()), "title": topic, "completed": False} 
                          for topic in CURRICULUM_DATA[name]]
            subject_doc = {
                "id": str(uuid.uuid4()),
                "name": name,
                "topics": topics_data
            }
            await db.subjects.insert_one(subject_doc)
        
        # Calculate stats
        total_topics = len(subject_doc["topics"])
        completed_topics = sum(1 for topic in subject_doc["topics"] if topic["completed"])
        completion_rate = (completed_topics / total_topics * 100) if total_topics > 0 else 0
        
        subjects.append({
            "id": subject_doc["id"],
            "name": subject_doc["name"], 
            "total_topics": total_topics,
            "completed_topics": completed_topics,
            "completion_rate": round(completion_rate, 1)
        })
    
    return subjects

@api_router.get("/subjects/{subject_name}/topics", response_model=List[Topic])
async def get_topics(subject_name: str):
    """Get all topics for a specific subject"""
    subject_doc = await db.subjects.find_one({"name": subject_name})
    if not subject_doc:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    return [Topic(**topic) for topic in subject_doc["topics"]]

@api_router.put("/subjects/{subject_name}/topics/{topic_id}")
async def toggle_topic_completion(subject_name: str, topic_id: str, update_data: TopicUpdate):
    """Toggle topic completion status"""
    subject_doc = await db.subjects.find_one({"name": subject_name})
    if not subject_doc:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    # Find and update the topic
    topics = subject_doc["topics"]
    topic_found = False
    for topic in topics:
        if topic["id"] == topic_id:
            topic["completed"] = update_data.completed  
            topic_found = True
            break
    
    if not topic_found:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    # Update in database
    await db.subjects.update_one(
        {"name": subject_name},
        {"$set": {"topics": topics}}
    )
    
    return {"message": "Topic updated successfully"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()