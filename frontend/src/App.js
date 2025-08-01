import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const HomePage = ({ onSubjectSelect }) => {
  const [subjects, setSubjects] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSubjects();
  }, []);

  const fetchSubjects = async () => {
    try {
      const response = await axios.get(`${API}/subjects`);
      setSubjects(response.data);
      setLoading(false);
    } catch (error) {
      console.error("Error fetching subjects:", error);
      setLoading(false);
    }
  };

  const getSubjectIcon = (subject) => {
    const icons = {
      "Türkçe": "📚",
      "Fizik": "⚛️", 
      "Kimya": "🧪",
      "Biyoloji": "🧬",
      "Matematik": "📐"
    };
    return icons[subject] || "📖";
  };

  const getCompletionColor = (rate) => {
    if (rate === 100) return "text-green-600";
    if (rate >= 70) return "text-blue-600";
    if (rate >= 40) return "text-yellow-600";
    return "text-purple-600";
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mx-auto mb-4"></div>
          <p className="text-purple-600 font-medium">Müfredat yükleniyor...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-800 mb-4">
            📋 Müfredat Takip Sistemi
          </h1>
          <p className="text-gray-600 text-lg">
            12. Sınıf müfredat konularını takip edin ve ilerleyişinizi görün
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
          {subjects.map((subject) => (
            <div
              key={subject.id}
              onClick={() => onSubjectSelect(subject.name)}
              className="stats-card bg-white rounded-2xl p-6 shadow-lg hover:shadow-xl transform hover:-translate-y-2 transition-all duration-300 cursor-pointer border-l-4 border-purple-500"
            >
              <div className="flex items-center justify-between mb-4">
                <div className="text-3xl">{getSubjectIcon(subject.name)}</div>
                <div className={`text-2xl font-bold ${getCompletionColor(subject.completion_rate)}`}>
                  {subject.completion_rate}%
                </div>
              </div>
              
              <h3 className="text-xl font-bold text-gray-800 mb-2">
                {subject.name}
              </h3>
              
              <div className="space-y-2">
                <div className="flex justify-between text-sm text-gray-600">
                  <span>Toplam Konu</span>
                  <span className="font-semibold">{subject.total_topics}</span>
                </div>
                <div className="flex justify-between text-sm text-gray-600">
                  <span>Tamamlanan</span>
                  <span className="font-semibold text-green-600">{subject.completed_topics}</span>
                </div>
                <div className="flex justify-between text-sm text-gray-600">
                  <span>Kalan</span>
                  <span className="font-semibold text-orange-600">
                    {subject.total_topics - subject.completed_topics}
                  </span>
                </div>
              </div>

              <div className="mt-4">
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-gradient-to-r from-purple-500 to-indigo-600 h-2 rounded-full transition-all duration-500"
                    style={{ width: `${subject.completion_rate}%` }}
                  ></div>
                </div>
              </div>

              <div className="mt-4 flex items-center justify-center">
                <button className="text-purple-600 hover:text-purple-800 font-medium text-sm flex items-center">
                  Konuları Görüntüle
                  <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

const SubjectDetail = ({ subjectName, onBack }) => {
  const [topics, setTopics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all"); // all, completed, pending

  useEffect(() => {
    fetchTopics();
  }, [subjectName]);

  const fetchTopics = async () => {
    try {
      const response = await axios.get(`${API}/subjects/${subjectName}/topics`);
      setTopics(response.data);
      setLoading(false);
    } catch (error) {
      console.error("Error fetching topics:", error);
      setLoading(false);
    }
  };

  const toggleTopic = async (topicId, currentStatus) => {
    try {
      await axios.put(`${API}/subjects/${subjectName}/topics/${topicId}`, {
        completed: !currentStatus
      });
      
      // Update local state
      setTopics(topics.map(topic => 
        topic.id === topicId 
          ? { ...topic, completed: !currentStatus }
          : topic
      ));
    } catch (error) {
      console.error("Error updating topic:", error);
    }
  };

  const getSubjectIcon = (subject) => {
    const icons = {
      "Türkçe": "📚",
      "Fizik": "⚛️", 
      "Kimya": "🧪",
      "Biyoloji": "🧬",
      "Matematik": "📐"
    };
    return icons[subject] || "📖";
  };

  const filteredTopics = topics.filter(topic => {
    if (filter === "completed") return topic.completed;
    if (filter === "pending") return !topic.completed;
    return true;
  });

  const stats = {
    total: topics.length,
    completed: topics.filter(t => t.completed).length,
    pending: topics.filter(t => !t.completed).length,
    percentage: topics.length > 0 ? Math.round((topics.filter(t => t.completed).length / topics.length) * 100) : 0
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mx-auto mb-4"></div>
          <p className="text-purple-600 font-medium">Konular yükleniyor...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={onBack}
            className="flex items-center text-purple-600 hover:text-purple-800 mb-4 font-medium"
          >
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Ana Sayfa
          </button>
          
          <div className="text-center">
            <div className="text-6xl mb-4">{getSubjectIcon(subjectName)}</div>
            <h1 className="text-4xl font-bold text-gray-800 mb-2">{subjectName}</h1>
            <p className="text-gray-600">Müfredat konularını tamamlayın</p>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8 max-w-4xl mx-auto">
          <div className="stats-card-total bg-white rounded-xl p-4 text-center shadow-lg">
            <div className="text-2xl font-bold text-purple-600">{stats.total}</div>
            <div className="text-sm text-gray-600">Toplam</div>
          </div>
          <div className="stats-card-completed bg-white rounded-xl p-4 text-center shadow-lg">
            <div className="text-2xl font-bold text-green-600">{stats.completed}</div>
            <div className="text-sm text-gray-600">Tamamlanan</div>
          </div>
          <div className="stats-card-pending bg-white rounded-xl p-4 text-center shadow-lg">
            <div className="text-2xl font-bold text-orange-600">{stats.pending}</div>
            <div className="text-sm text-gray-600">Kalan</div>
          </div>
          <div className="stats-card-percentage bg-white rounded-xl p-4 text-center shadow-lg">
            <div className="text-2xl font-bold text-blue-600">{stats.percentage}%</div>
            <div className="text-sm text-gray-600">Tamamlama</div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="max-w-4xl mx-auto mb-8">
          <div className="bg-white rounded-xl p-6 shadow-lg">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium text-gray-700">İlerleme</span>
              <span className="text-sm font-medium text-purple-600">{stats.percentage}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className="bg-gradient-to-r from-purple-500 to-indigo-600 h-3 rounded-full transition-all duration-500"
                style={{ width: `${stats.percentage}%` }}
              ></div>
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="max-w-4xl mx-auto mb-6">
          <div className="flex justify-center space-x-2">
            <button
              onClick={() => setFilter("all")}
              className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                filter === "all" 
                  ? "bg-purple-500 text-white" 
                  : "bg-white text-gray-600 hover:bg-purple-100"
              }`}
            >
              Tümü ({stats.total})
            </button>
            <button
              onClick={() => setFilter("pending")}
              className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                filter === "pending" 
                  ? "bg-orange-500 text-white" 
                  : "bg-white text-gray-600 hover:bg-orange-100"
              }`}
            >
              Bekleyen ({stats.pending})
            </button>
            <button
              onClick={() => setFilter("completed")}
              className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                filter === "completed" 
                  ? "bg-green-500 text-white" 
                  : "bg-white text-gray-600 hover:bg-green-100"
              }`}
            >
              Tamamlanan ({stats.completed})
            </button>
          </div>
        </div>

        {/* Topics List */}
        <div className="max-w-4xl mx-auto">
          <div className="space-y-3">
            {filteredTopics.map((topic, index) => (
              <div
                key={topic.id}
                className={`bg-white rounded-xl p-4 shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-200 ${
                  topic.completed ? "bg-green-50 border-l-4 border-green-500" : "border-l-4 border-purple-500"
                }`}
              >
                <div className="flex items-center">
                  <div className="flex-shrink-0 mr-4">
                    <button
                      onClick={() => toggleTopic(topic.id, topic.completed)}
                      className={`w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all ${
                        topic.completed
                          ? "bg-green-500 border-green-500 text-white"
                          : "border-gray-300 hover:border-purple-500"
                      }`}
                    >
                      {topic.completed && (
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                      )}
                    </button>
                  </div>
                  
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-500 font-medium">
                        Konu {index + 1}
                      </span>
                      {topic.completed && (
                        <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full font-medium">
                          ✓ Tamamlandı
                        </span>
                      )}
                    </div>
                    <h3 className={`text-lg font-medium mt-1 ${
                      topic.completed 
                        ? "text-gray-500 line-through" 
                        : "text-gray-800"
                    }`}>
                      {topic.title}
                    </h3>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {filteredTopics.length === 0 && (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">🔍</div>
              <h3 className="text-xl font-medium text-gray-600 mb-2">
                {filter === "completed" && "Henüz tamamlanmış konu yok"}
                {filter === "pending" && "Tüm konular tamamlanmış! 🎉"}
                {filter === "all" && "Konu bulunamadı"}
              </h3>
              <p className="text-gray-500">
                {filter === "completed" && "Konuları tamamladıkça burada görünecekler"}
                {filter === "pending" && "Harika iş çıkardın!"}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

function App() {
  const [currentView, setCurrentView] = useState("home");
  const [selectedSubject, setSelectedSubject] = useState(null);

  const handleSubjectSelect = (subjectName) => {
    setSelectedSubject(subjectName);
    setCurrentView("subject");
  };

  const handleBackToHome = () => {
    setCurrentView("home");
    setSelectedSubject(null);
  };

  return (
    <div className="App">
      {currentView === "home" && (
        <HomePage onSubjectSelect={handleSubjectSelect} />
      )}
      {currentView === "subject" && (
        <SubjectDetail 
          subjectName={selectedSubject} 
          onBack={handleBackToHome} 
        />
      )}
    </div>
  );
}

export default App;