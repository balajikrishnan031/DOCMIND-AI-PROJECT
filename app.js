/* DocMind AI - Application Controller */

// Initialize PDF.js worker
pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.4.120/pdf.worker.min.js';

// --- CONFIGURATION & DATABASE STATE ---
const DB_NAME = 'DocMindAI_DB';
const DB_VERSION = 1;
let db = null;

// Python Backend URL configuration
const BACKEND_URL = 'http://localhost:5000';

// Global application state
const state = {
  documents: [],
  folders: [],
  tags: [],
  activeDocId: null,
  activeView: 'landing', // 'landing', 'dashboard', 'reader', 'f-lectures', 'f-exam', 'f-research', 'f-syllabus', 'f-records', 'f-reference'
  filters: {
    folderId: null,
    tag: null,
    search: ''
  },
  settings: {
    geminiKey: '',
    theme: 'dark'
  },
  chats: {}, // docId -> list of messages
  parsingQueue: new Set(), // docIds being processed
  backendOnline: false
};

// Colors list matching folder modal selections (6 distinct colors)
const FOLDER_COLORS = [
  'hsl(38, 90%, 55%)',  // Sand Gold
  'hsl(22, 90%, 55%)',  // Sunset Orange
  'hsl(346, 85%, 62%)', // Coral Pink
  'hsl(175, 80%, 45%)', // Soft Teal
  'hsl(180, 80%, 70%)', // Seafoam Aqua
  'hsl(142, 60%, 48%)'  // Emerald Green
];

// Stop words for local NLP fallback processing
const STOP_WORDS = new Set([
  'the', 'and', 'a', 'to', 'of', 'in', 'is', 'that', 'it', 'on', 'for', 'this', 'with', 'as', 'are', 'was', 'by', 'an', 'be', 'at', 'or', 'from', 'but', 'not', 'your', 'my', 'have', 'has', 'had', 'we', 'they', 'he', 'she', 'you', 'i', 'me', 'us', 'them', 'their', 'his', 'her', 'its', 'about', 'who', 'which', 'what', 'where', 'when', 'why', 'how', 'can', 'will', 'would', 'could', 'should', 'there', 'their', 'then', 'than', 'some', 'any', 'each', 'all', 'more', 'most', 'other', 'been', 'were', 'into', 'out', 'up', 'down', 'only', 'very', 'just', 'no', 'so', 'through', 'over', 'page', 'pdf', 'document', 'using', 'also', 'many', 'some', 'our'
]);

// Interactive Study Flashcards Mock Deck
const FLASHCARDS = [
  { q: "What does TF-IDF calculate in NLP?", a: "Term Frequency - Inverse Document Frequency. It measures how unique and important a term is relative to all pages in a document." },
  { q: "How does the Similarity Chat select answers?", a: "It tokenizes your query, computes overlap dot-products against sentence vectors, and ranks matching context lines." },
  { q: "Where does DocMind store data offline?", a: "It uses client-side IndexedDB databases, ensuring 100% privacy and local storage for parsed note arrays and message histories." }
];
let currentFlashcardIndex = 0;

// Interactive Reference Glossary Mock Index
const GLOSSARY_ITEMS = [
  { term: "Artificial Intelligence (AI)", letter: "A", def: "Software executing cognitive tasks such as document parsing, term statistics, and similarity queries." },
  { term: "Auditing Ledger", letter: "A", def: "A structured ledger view representing records index rows, sizes, and file analysis status tags." },
  { term: "Cosine Similarity", letter: "C", def: "A vector matching formula used to measure terms overlap between questions and document text vectors." },
  { term: "Citation Bibliography", letter: "C", def: "A formatted reference index block (APA/MLA/Chicago) generated to cite academic notes." },
  { term: "Document Ingestion", letter: "D", def: "The process of extracting readable text pages directly in the browser via PDF.js worker buffers." },
  { term: "Extractive Summarizer", letter: "E", def: "An NLP pipeline calculating sentence importance scores to compile key takeaways checklists." },
  { term: "Frequency Counts (TF)", letter: "F", def: "The count of word occurrences inside document text pages, scoring key keywords." },
  { term: "Glossary Shelf", letter: "G", def: "An interactive index panel categorizing technical terminology alphabetically (A-Z)." },
  { term: "Information Density Index", letter: "I", def: "An audit percentage highlighting text complexity based on keyword densities." },
  { term: "Inverse Document Frequency (IDF)", letter: "I", def: "Statistical measure penalizing common words across pages to highlight topic keywords." },
  { term: "Keywords Extraction", letter: "K", def: "Identifying primary topics by filtering stopwords and ranking term occurrences." },
  { term: "Localhost Integration", letter: "L", def: "Running document processing modules locally on port 5000 to keep note files private." },
  { term: "Milestone Deadlines", letter: "M", def: "Checking off assignment due dates and preparation targets from course planners." },
  { term: "Notebook Binder View", letter: "N", def: "A visual workspace presenting lecture slides inside a lined spiral notebook layout." },
  { term: "Syllabus Indexing", letter: "S", def: "Mapping dates and course requirements from syllabus schedules into timetable slots." },
  { term: "Term Overlap", letter: "T", def: "Matching shared words between query strings and sentences to locate answer blocks." }
];

// --- DATABASE OPERATIONS (IndexedDB) ---

function initDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);

    request.onerror = (event) => {
      showToast('Database failed to initialize: ' + event.target.error, 'danger');
      reject(event.target.error);
    };

    request.onsuccess = (event) => {
      db = event.target.result;
      resolve(db);
    };

    request.onupgradeneeded = (event) => {
      const database = event.target.result;
      
      if (!database.objectStoreNames.contains('documents')) {
        database.createObjectStore('documents', { keyPath: 'id' });
      }
      
      if (!database.objectStoreNames.contains('folders')) {
        database.createObjectStore('folders', { keyPath: 'id' });
      }

      if (!database.objectStoreNames.contains('tags')) {
        database.createObjectStore('tags', { keyPath: 'name' });
      }

      if (!database.objectStoreNames.contains('settings')) {
        database.createObjectStore('settings', { keyPath: 'key' });
      }
      
      if (!database.objectStoreNames.contains('chats')) {
        database.createObjectStore('chats', { keyPath: 'docId' });
      }
    };
  });
}

function dbSave(storeName, item) {
  return new Promise((resolve, reject) => {
    if (!db) return reject('No DB connection');
    const transaction = db.transaction([storeName], 'readwrite');
    const store = transaction.objectStore(storeName);
    const request = store.put(item);
    request.onsuccess = () => resolve(item);
    request.onerror = (e) => reject(e.target.error);
  });
}

function dbGetAll(storeName) {
  return new Promise((resolve, reject) => {
    if (!db) return reject('No DB connection');
    const transaction = db.transaction([storeName], 'readonly');
    const store = transaction.objectStore(storeName);
    const request = store.getAll();
    request.onsuccess = () => resolve(request.result);
    request.onerror = (e) => reject(e.target.error);
  });
}

function dbDelete(storeName, key) {
  return new Promise((resolve, reject) => {
    if (!db) return reject('No DB connection');
    const transaction = db.transaction([storeName], 'readwrite');
    const store = transaction.objectStore(storeName);
    const request = store.delete(key);
    request.onsuccess = () => resolve(key);
    request.onerror = (e) => reject(e.target.error);
  });
}

function dbGet(storeName, key) {
  return new Promise((resolve, reject) => {
    if (!db) return reject('No DB connection');
    const transaction = db.transaction([storeName], 'readonly');
    const store = transaction.objectStore(storeName);
    const request = store.get(key);
    request.onsuccess = () => resolve(request.result);
    request.onerror = (e) => reject(e.target.error);
  });
}

// --- APP INITIALIZATION ---

document.addEventListener('DOMContentLoaded', async () => {
  try {
    await initDB();
    await loadStateFromDB();
    setupEventListeners();
    applyTheme(state.settings.theme);
    populateFolderDropdowns();
    populateTagDropdowns();
    renderSidebar();
    renderDashboard();
    updateStats();
    updateApiStatusBadge();
    checkStorageUsage();
    checkBackendHealth();
    setupScrollReveal();
  } catch (error) {
    console.error('Initialization error:', error);
  }
});

async function loadStateFromDB() {
  state.documents = await dbGetAll('documents') || [];
  state.folders = await dbGetAll('folders') || [];
  state.tags = await dbGetAll('tags') || [];
  
  const storedTheme = await dbGet('settings', 'theme');
  const storedGeminiKey = await dbGet('settings', 'geminiKey');
  state.settings.theme = storedTheme ? storedTheme.value : 'dark';
  state.settings.geminiKey = storedGeminiKey ? storedGeminiKey.value : '';

  if (state.folders.length === 0) {
    const defaults = [
      { id: 'f-lectures', name: 'Lecture Notes', color: 'hsl(38, 90%, 55%)' },
      { id: 'f-exam', name: 'Study Guides', color: 'hsl(22, 90%, 55%)' },
      { id: 'f-research', name: 'Research Papers', color: 'hsl(346, 85%, 62%)' },
      { id: 'f-syllabus', name: 'Syllabus Planners', color: 'hsl(175, 80%, 45%)' },
      { id: 'f-records', name: 'Office Records', color: 'hsl(180, 80%, 70%)' },
      { id: 'f-reference', name: 'Reference Guides', color: 'hsl(142, 60%, 48%)' }
    ];
    for (const f of defaults) {
      await dbSave('folders', f);
      state.folders.push(f);
    }
  } else {
    // Force override color schemes of existing folders to prevent multi-color clash
    const folderColorMapping = {
      'f-lectures': 'hsl(38, 90%, 55%)',
      'f-exam': 'hsl(22, 90%, 55%)',
      'f-research': 'hsl(346, 85%, 62%)',
      'f-syllabus': 'hsl(175, 80%, 45%)',
      'f-records': 'hsl(180, 80%, 70%)',
      'f-reference': 'hsl(142, 60%, 48%)'
    };
    for (let f of state.folders) {
      if (folderColorMapping[f.id] && f.color !== folderColorMapping[f.id]) {
        f.color = folderColorMapping[f.id];
        await dbSave('folders', f);
      }
    }
  }

  if (state.tags.length === 0) {
    const defaults = [
      { name: 'Priority' },
      { name: 'Reference' },
      { name: 'Syllabus' }
    ];
    for (const t of defaults) {
      await dbSave('tags', t);
      state.tags.push(t);
    }
  }
}

// --- SCROLL REVEAL TIMELINE ANIMATION ---

function setupScrollReveal() {
  if (!('IntersectionObserver' in window)) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
      }
    });
  }, { threshold: 0.15 });

  document.querySelectorAll('.feature-slide-card').forEach(card => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(40px)';
    card.style.transition = 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
    observer.observe(card);
  });
}

// --- PYTHON BACKEND HEALTH CHECK ---

async function checkBackendHealth() {
  try {
    const res = await fetch(`${BACKEND_URL}/api/health`, { method: 'GET' });
    if (res.ok) {
      state.backendOnline = true;
      console.log('Python NLP Backend is ONLINE');
      updateApiStatusBadge();
    }
  } catch (e) {
    state.backendOnline = false;
    console.log('Python NLP Backend is OFFLINE (falling back to client-side)');
    updateApiStatusBadge();
  }
}

// --- THEME & STATUS CONTROLLERS ---

function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  const themeBtn = document.getElementById('btn-theme-toggle');
  
  if (theme === 'light') {
    themeBtn.innerHTML = '<i class="fa-solid fa-sun"></i>';
    themeBtn.title = 'Switch to Dark Theme';
  } else {
    themeBtn.innerHTML = '<i class="fa-solid fa-moon"></i>';
    themeBtn.title = 'Switch to Light Theme';
  }
  
  themeBtn.classList.add('theme-rotate');
  setTimeout(() => themeBtn.classList.remove('theme-rotate'), 450);
}

function updateApiStatusBadge() {
  const badge = document.getElementById('api-status-badge');
  if (!badge) return;

  if (state.backendOnline) {
    badge.className = '';
    badge.style.backgroundColor = 'hsla(142, 70%, 45%, 0.15)';
    badge.style.color = 'var(--success)';
    badge.style.border = '1px solid hsla(142, 70%, 45%, 0.3)';
    badge.innerHTML = '<i class="fa-brands fa-python"></i> Python Backend Active';
  } else if (state.settings.geminiKey) {
    badge.className = '';
    badge.style.backgroundColor = 'hsla(43, 90%, 60%, 0.15)';
    badge.style.color = 'var(--accent-gold)';
    badge.style.border = '1px solid hsla(43, 90%, 60%, 0.3)';
    badge.innerHTML = '<i class="fa-solid fa-bolt"></i> Gemini API Live';
  } else {
    badge.className = '';
    badge.style.backgroundColor = 'rgba(255, 255, 255, 0.05)';
    badge.style.color = 'var(--text-muted)';
    badge.style.border = '1px solid var(--border-color)';
    badge.innerHTML = '<i class="fa-solid fa-microchip"></i> Local NLP Fallback';
  }
}

async function checkStorageUsage() {
  if (!navigator.storage || !navigator.storage.estimate) {
    document.getElementById('storage-text').textContent = 'Storage: Active';
    document.getElementById('storage-bar').style.width = '15%';
    return;
  }
  const estimate = await navigator.storage.estimate();
  const used = estimate.usage || 0;
  const quota = estimate.quota || 100 * 1024 * 1024;
  
  const maxLimit = 50 * 1024 * 1024; 
  const displayUsed = Math.min(used, maxLimit);
  const percent = Math.min((displayUsed / maxLimit) * 100, 100);
  
  document.getElementById('storage-text').textContent = `${formatSize(displayUsed)} / ${formatSize(maxLimit)}`;
  document.getElementById('storage-bar').style.width = percent + '%';
}

function formatSize(bytes) {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

// --- NLP & AI CORE (HYBRID MODEL) ---

async function requestGeminiAPI(prompt, systemInstruction = '') {
  const key = state.settings.geminiKey;
  if (!key) throw new Error('API Key missing');

  const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${key}`;
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      contents: [{
        role: 'user',
        parts: [{ text: prompt }]
      }],
      systemInstruction: systemInstruction ? {
        parts: [{ text: systemInstruction }]
      } : undefined,
      generationConfig: { temperature: 0.4, maxOutputTokens: 800 }
    })
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.error?.message || 'API request failed');
  }

  const data = await response.json();
  return data.candidates[0].content.parts[0].text;
}

async function analyzeParsedDocument(docTitle, pagesText) {
  if (state.backendOnline) {
    try {
      showToast('Analyzing text using Python NLP Server...', 'info');
      const response = await fetch(`${BACKEND_URL}/api/upload`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: docTitle,
          textPages: pagesText
        })
      });
      if (response.ok) {
        return await response.json();
      } else {
        throw new Error('Python server processing failed');
      }
    } catch (e) {
      console.warn('Python backend upload failed, falling back:', e);
    }
  }

  if (state.settings.geminiKey) {
    try {
      showToast('Processing document with Gemini AI...', 'info');
      const fullText = pagesText.join('\n').slice(0, 18000);
      
      const analysisPrompt = `
      Analyze this PDF text content:
      Document Title: "${docTitle}"
      
      Generate a structured JSON output with the keys: "summary", "takeaways", "keywords".
      - "summary": A readable 2-paragraph overview outlining the themes of these notes.
      - "takeaways": An array of exactly 5 bullet points capturing key formulas or principles.
      - "keywords": An array of exactly 10 distinct keywords found in the text.
      
      Text Context:
      ${fullText}
      
      Return ONLY the JSON block. Do not wrap in markdown tags.
      `;

      const responseText = await requestGeminiAPI(analysisPrompt, 'You are an academic text parser. Output raw JSON only.');
      const cleanedJSON = responseText.replace(/```json/g, '').replace(/```/g, '').trim();
      return JSON.parse(cleanedJSON);
    } catch (e) {
      console.warn('Gemini extraction failed, using Offline Engine:', e);
      showToast('Gemini API failed, using local offline NLP analyzer', 'warning');
    }
  }

  return performOfflineNLPAnalysis(docTitle, pagesText);
}

function performOfflineNLPAnalysis(docTitle, pagesText) {
  const fullText = pagesText.join('\n');
  const words = fullText.toLowerCase().match(/[a-z]{3,15}/g) || [];
  const freqMap = {};
  
  words.forEach(w => {
    if (!STOP_WORDS.has(w)) freqMap[w] = (freqMap[w] || 0) + 1;
  });

  const sortedKeywords = Object.entries(freqMap)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)
    .map(entry => entry[0]);

  if (sortedKeywords.length === 0) {
    sortedKeywords.push('document', 'notes', 'study', 'content', 'pdf');
  }

  const sentences = fullText.split(/[.!?]\s+/).map(s => s.trim()).filter(s => s.length > 25 && s.length < 200);
  const scoredSentences = sentences.map(sentence => {
    let score = 0;
    const tokens = sentence.toLowerCase().match(/[a-z]+/g) || [];
    tokens.forEach(tok => {
      if (sortedKeywords.includes(tok)) score += 5;
      if (freqMap[tok]) score += freqMap[tok];
    });
    score = score / Math.max(1, tokens.length);
    return { text: sentence, score };
  });

  const topTakeaways = scoredSentences
    .sort((a, b) => b.score - a.score)
    .slice(0, 5)
    .map(item => item.text.replace(/\n/g, ' ').replace(/\s+/g, ' ') + '.');

  while (topTakeaways.length < 5) {
    topTakeaways.push(`Contains technical content outlining concepts related to ${sortedKeywords.slice(0, 3).join(', ')}.`);
  }

  const topWordsFormatted = sortedKeywords.slice(0, 5).map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(', ');
  const summaryParagraph1 = `This document titled "${docTitle}" spans ${pagesText.length} page(s) and centers heavily around key concepts, including ${topWordsFormatted}. The material serves as an informative educational guide suitable for students, educators, or professionals looking to master these technical topics.`;
  const summaryParagraph2 = `Main highlights in the text focus on: "${topTakeaways[0]}" and "${topTakeaways[1]}". The notes present structured summaries that help clarify the core principles of the subject matter.`;

  return {
    summary: `${summaryParagraph1}\n\n${summaryParagraph2}`,
    takeaways: topTakeaways,
    keywords: sortedKeywords
  };
}

async function answerQuestionAboutDocument(doc, question) {
  if (state.backendOnline) {
    try {
      const response = await fetch(`${BACKEND_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          documentId: doc.id,
          question: question,
          textPages: doc.textPages
        })
      });
      if (response.ok) {
        const result = await response.json();
        return result.answer;
      } else {
        throw new Error('Python chat query failed');
      }
    } catch (e) {
      console.warn('Python backend chat query failed, falling back:', e);
    }
  }

  if (state.settings.geminiKey) {
    try {
      const systemInstruction = `
      You are DocMind AI, a helpful virtual assistant.
      The user is asking questions about the document: "${doc.name}"
      Answer the question accurately using the document text context provided.
      If the answer cannot be found or inferred from the text, state that clearly.
      `;
      
      const prompt = `
      Document Context:
      ${doc.textPages.join('\n').slice(0, 20000)}
      
      User's Question: "${question}"
      `;

      return await requestGeminiAPI(prompt, systemInstruction);
    } catch (e) {
      console.warn('Gemini chat failed, using local search answering:', e);
    }
  }

  return performLocalSearchAnswering(doc, question);
}

function performLocalSearchAnswering(doc, question) {
  const queryWords = question.toLowerCase().match(/[a-z]{3,15}/g) || [];
  if (queryWords.length === 0) {
    return "I couldn't identify any searchable terms in your question. Could you please specify what information you are looking for?";
  }

  let bestPageIdx = 0;
  let highestScore = -1;

  doc.textPages.forEach((pageText, idx) => {
    let score = 0;
    const pageLower = pageText.toLowerCase();
    queryWords.forEach(word => {
      if (STOP_WORDS.has(word)) return;
      const count = (pageLower.split(word).length - 1);
      score += count * 10;
    });
    if (score > highestScore) {
      highestScore = score;
      bestPageIdx = idx;
    }
  });

  const bestPageText = doc.textPages[bestPageIdx];
  const paragraphs = bestPageText.split(/\n\n+/).map(p => p.trim()).filter(p => p.length > 30);
  let bestParagraph = '';
  let bestParaScore = -1;

  paragraphs.forEach(para => {
    let score = 0;
    const paraLower = para.toLowerCase();
    queryWords.forEach(word => {
      if (paraLower.includes(word)) score += 5;
    });
    if (score > bestParaScore) {
      bestParaScore = score;
      bestParagraph = para;
    }
  });

  const highlightContent = bestParagraph || bestPageText.slice(0, 300) + '...';

  if (highestScore > 0) {
    return `**Offline Local Analysis (Matching Page ${bestPageIdx + 1}):**\n\nI found a matching section in the document on **Page ${bestPageIdx + 1}** regarding your question:\n\n> "${highlightContent.replace(/\n/g, ' ')}"\n\n*Note: Start python server to enable complete semantic TF-IDF query models.*`;
  } else {
    const mainKeywords = doc.keywords.slice(0, 4).join(', ');
    return `I searched through the document but could not find a strong textual correlation to your query: "${question}". \n\nHowever, this document focuses on **${mainKeywords}**.`;
  }
}

// --- PDF PROCESSING ---

async function parseAndRegisterPDF(file, folderId = null, tag = null) {
  const docId = 'doc-' + Date.now();
  state.parsingQueue.add(docId);

  const dummyDoc = {
    id: docId,
    name: file.name,
    size: file.size,
    uploadDate: new Date().toLocaleDateString(),
    folderId: folderId,
    tags: tag ? [tag] : [],
    textPages: [],
    summary: 'Parsing text content...',
    takeaways: [],
    keywords: [],
    isParsing: true
  };

  state.documents.unshift(dummyDoc);
  
  if (state.activeView === 'dashboard' || state.activeView === 'landing') {
    renderDashboard();
  } else {
    renderSpace(state.activeView);
  }
  
  showToast(`Uploading and analyzing ${file.name}...`, 'info');

  try {
    const arrayBuffer = await readFileAsArrayBuffer(file);
    const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
    const pageTexts = [];

    for (let i = 1; i <= pdf.numPages; i++) {
      const page = await pdf.getPage(i);
      const textContent = await page.getTextContent();
      const pageText = textContent.items.map(item => item.str).join(' ');
      pageTexts.push(pageText);
    }

    if (pageTexts.join('').trim().length === 0) {
      throw new Error("This PDF seems to contain only images or no readable text.");
    }

    const analytics = await analyzeParsedDocument(file.name, pageTexts);

    const fullDoc = {
      ...dummyDoc,
      textPages: pageTexts,
      summary: analytics.summary,
      takeaways: analytics.takeaways,
      keywords: analytics.keywords,
      isParsing: false
    };

    const idx = state.documents.findIndex(d => d.id === docId);
    if (idx !== -1) {
      state.documents[idx] = fullDoc;
    }
    
    await dbSave('documents', fullDoc);
    state.parsingQueue.delete(docId);
    
    showToast(`Successfully analyzed ${file.name}!`, 'success');
    
    if (state.activeView === 'dashboard') {
      renderDashboard();
    } else {
      renderSpace(state.activeView);
    }
    
    updateStats();
    checkStorageUsage();
  } catch (error) {
    console.error('PDF extraction failed:', error);
    showToast(`Error reading ${file.name}: ` + error.message, 'danger');
    
    state.documents = state.documents.filter(d => d.id !== docId);
    state.parsingQueue.delete(docId);
    
    if (state.activeView === 'dashboard') {
      renderDashboard();
    } else {
      renderSpace(state.activeView);
    }
  }
}

function readFileAsArrayBuffer(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = () => reject(reader.error);
    reader.readAsArrayBuffer(file);
  });
}

// --- DOM RENDERING & VIEW CONTROLLERS ---

function renderSidebar() {
  const foldersContainer = document.getElementById('folders-list');
  foldersContainer.innerHTML = '';
  
  const allLi = document.createElement('li');
  allLi.className = 'folder-item';
  allLi.innerHTML = `
    <button class="folder-item-btn ${state.filters.folderId === null ? 'active' : ''}" id="btn-folder-all">
      <span class="folder-name-container">
        <i class="fa-solid fa-folder-open" style="color: var(--accent-gold);"></i>
        All Notes
      </span>
      <span class="folder-count">${state.documents.length}</span>
    </button>
  `;
  foldersContainer.appendChild(allLi);

  document.getElementById('btn-folder-all').addEventListener('click', () => {
    state.filters.folderId = null;
    state.filters.tag = null;
    document.querySelectorAll('.tag-pill').forEach(p => p.classList.remove('active'));
    switchView('dashboard');
    renderSidebar();
    renderDashboard();
  });

  state.folders.forEach(folder => {
    const docCount = state.documents.filter(d => d.folderId === folder.id).length;
    const li = document.createElement('li');
    li.className = 'folder-item';
    li.innerHTML = `
      <button class="folder-item-btn ${state.filters.folderId === folder.id ? 'active' : ''}" data-id="${folder.id}">
        <span class="folder-name-container">
          <span class="folder-color-dot" style="background-color: ${folder.color};"></span>
          ${folder.name}
        </span>
        <span class="folder-count">${docCount}</span>
      </button>
    `;
    foldersContainer.appendChild(li);

    li.querySelector('button').addEventListener('click', () => {
      state.filters.folderId = folder.id;
      state.filters.tag = null;
      document.querySelectorAll('.tag-pill').forEach(p => p.classList.remove('active'));
      switchView(folder.id);
      renderSidebar();
    });
  });

  const tagsContainer = document.getElementById('tags-list');
  tagsContainer.innerHTML = '';
  state.tags.forEach(tag => {
    const tagBtn = document.createElement('button');
    tagBtn.className = `tag-pill ${state.filters.tag === tag.name ? 'active' : ''}`;
    tagBtn.textContent = `#${tag.name}`;
    tagBtn.addEventListener('click', () => {
      if (state.filters.tag === tag.name) {
        state.filters.tag = null;
      } else {
        state.filters.tag = tag.name;
        state.filters.folderId = null;
      }
      switchView('dashboard');
      renderSidebar();
      renderDashboard();
    });
    tagsContainer.appendChild(tagBtn);
  });
}

function renderDashboard() {
  const grid = document.getElementById('document-grid');
  const emptyState = document.getElementById('dashboard-empty-state');
  if (!grid) return;
  grid.innerHTML = '';

  let filtered = [...state.documents];
  
  if (state.filters.search.trim()) {
    const q = state.filters.search.toLowerCase();
    filtered = filtered.filter(d => 
      d.name.toLowerCase().includes(q) || 
      d.textPages.some(page => page.toLowerCase().includes(q))
    );
  }

  const headerText = document.getElementById('doc-grid-header-text');
  const filterIndicator = document.getElementById('filter-indicator');
  const filterText = document.getElementById('filter-text');

  if (state.filters.tag || state.filters.search) {
    if (filterIndicator) filterIndicator.style.display = 'flex';
    let filterMsg = 'Filters active: ';
    if (state.filters.tag) {
      filterMsg += `Tag: #${state.filters.tag}`;
    }
    if (state.filters.search) {
      filterMsg += `${state.filters.tag ? ' + ' : ''}Search: "${state.filters.search}"`;
    }
    if (filterText) filterText.textContent = filterMsg;
    if (headerText) headerText.innerHTML = `<i class="fa-solid fa-filter"></i> Filtered Results (${filtered.length})`;
  } else {
    if (filterIndicator) filterIndicator.style.display = 'none';
    if (headerText) headerText.innerHTML = `<i class="fa-solid fa-clock-rotate-left"></i> Recent Materials`;
  }

  if (filtered.length === 0) {
    if (emptyState) emptyState.style.display = 'flex';
  } else {
    if (emptyState) emptyState.style.display = 'none';
  }

  filtered.forEach(doc => {
    const folder = state.folders.find(f => f.id === doc.folderId);
    const sizeKB = (doc.size / 1024).toFixed(1);
    
    const card = document.createElement('div');
    card.className = 'document-card';
    card.setAttribute('data-id', doc.id);

    let badgesHTML = '';
    if (folder) {
      badgesHTML += `<span class="doc-badge doc-badge-folder" style="background-color: ${folder.color}22; color: ${folder.color};">${folder.name}</span>`;
    }
    doc.tags.forEach(t => {
      badgesHTML += `<span class="doc-badge doc-badge-tag">#${t}</span>`;
    });

    card.innerHTML = `
      ${doc.isParsing ? `
        <div class="scanning-overlay">
          <div class="scanning-spinner"></div>
          <span class="scanning-text">AI is reading...</span>
        </div>
      ` : ''}
      <div class="doc-card-header">
        <i class="fa-solid fa-file-pdf doc-card-icon"></i>
        <div class="doc-card-actions" onclick="event.stopPropagation();">
          <button class="doc-card-action-btn delete-doc" title="Delete document">
            <i class="fa-solid fa-trash-can"></i>
          </button>
        </div>
      </div>
      <h4 class="doc-card-title" title="${doc.name}">${doc.name}</h4>
      <div class="doc-card-badges">${badgesHTML}</div>
      <div class="doc-card-meta">
        <span>${sizeKB} KB</span>
        <span>${doc.uploadDate}</span>
      </div>
    `;

    card.addEventListener('click', () => {
      if (!doc.isParsing) {
        openDocumentInReader(doc.id);
      }
    });

    card.querySelector('.delete-doc').addEventListener('click', async (e) => {
      e.stopPropagation();
      if (confirm(`Are you sure you want to delete "${doc.name}"?`)) {
        await deleteDocument(doc.id);
      }
    });

    grid.appendChild(card);
  });
}

// --- CATEGORY WORKSPACE RENDERER ---

function renderSpace(folderId) {
  const folder = state.folders.find(f => f.id === folderId);
  if (!folder) return;

  const docs = state.documents.filter(d => d.folderId === folderId);
  
  // A. Generic updates: document lists for that category
  let gridId = '';
  let emptyId = '';
  
  switch(folderId) {
    case 'f-lectures': gridId = 'lectures-grid'; emptyId = 'lectures-empty-state'; break;
    case 'f-exam': gridId = 'study-grid'; emptyId = 'study-empty-state'; break;
    case 'f-research': gridId = 'research-grid'; emptyId = 'research-empty-state'; break;
    case 'f-syllabus': gridId = 'syllabus-grid'; emptyId = 'syllabus-empty-state'; break;
    case 'f-records': gridId = 'office-grid'; emptyId = 'office-empty-state'; break;
    case 'f-reference': gridId = 'reference-grid'; emptyId = 'reference-empty-state'; break;
  }

  const spaceGrid = document.getElementById(gridId);
  const spaceEmpty = document.getElementById(emptyId);

  if (spaceGrid) {
    spaceGrid.innerHTML = '';
    if (docs.length === 0) {
      if (spaceEmpty) spaceEmpty.style.display = 'block';
    } else {
      if (spaceEmpty) spaceEmpty.style.display = 'none';
      docs.forEach(doc => {
        const sizeKB = (doc.size / 1024).toFixed(1);
        const card = document.createElement('div');
        card.className = 'document-card';
        card.innerHTML = `
          ${doc.isParsing ? `
            <div class="scanning-overlay">
              <div class="scanning-spinner"></div>
              <span class="scanning-text">Analyzing...</span>
            </div>
          ` : ''}
          <div class="doc-card-header">
            <i class="fa-solid fa-file-pdf doc-card-icon"></i>
            <button class="doc-card-action-btn delete-doc" title="Delete document" onclick="event.stopPropagation();">
              <i class="fa-solid fa-trash-can"></i>
            </button>
          </div>
          <h4 class="doc-card-title" title="${doc.name}" style="font-size: 0.85rem;">${doc.name}</h4>
          <div class="doc-card-meta">
            <span>${sizeKB} KB</span>
          </div>
        `;
        card.addEventListener('click', () => {
          if (!doc.isParsing) openDocumentInReader(doc.id);
        });
        card.querySelector('.delete-doc').addEventListener('click', async (e) => {
          e.stopPropagation();
          if (confirm(`Delete "${doc.name}"?`)) {
            await deleteDocument(doc.id);
          }
        });
        spaceGrid.appendChild(card);
      });
    }
  }

  // B. Specific category visual widgets updates
  if (folderId === 'f-lectures') {
    document.getElementById('num-lecture-notes').textContent = docs.length;
    const highlights = document.getElementById('notebook-terms-highlights');
    if (docs.length > 0) {
      const allKeywords = docs.flatMap(d => d.keywords).slice(0, 8);
      const uniqueKeywords = [...new Set(allKeywords)];
      if (uniqueKeywords.length > 0) {
        highlights.innerHTML = '<p><strong>Extracted Highlights:</strong></p><div style="display:flex; flex-wrap:wrap; gap:8px; margin-top:8px;">' +
          uniqueKeywords.map(k => `<span class="tag-pill active" style="font-family:'Dancing Script', cursive; font-size:1rem;">#${k}</span>`).join('') +
          '</div>';
      }
    } else {
      highlights.innerHTML = 'No files parsed in this notebook section yet.';
    }
  } 
  
  else if (folderId === 'f-exam') {
    // Sync flashcard deck text
    updateStudyFlashcard();
  } 
  
  else if (folderId === 'f-research') {
    // Populate research dropdown selector
    const select = document.getElementById('citation-doc-select');
    if (select) {
      select.innerHTML = '';
      if (docs.length === 0) {
        select.innerHTML = '<option value="">No papers uploaded yet</option>';
        document.getElementById('citation-result-box').textContent = 'Please upload a paper to format bibliography logs.';
        document.getElementById('research-abstract-preview').textContent = 'Upload articles to index technical summaries and citation codes.';
      } else {
        docs.forEach(doc => {
          const opt = document.createElement('option');
          opt.value = doc.id;
          opt.textContent = doc.name;
          select.appendChild(opt);
        });
        updateResearchCitation();
      }
    }
  } 
  
  else if (folderId === 'f-records') {
    // Render office spreadsheets table
    const tableBody = document.getElementById('ledger-files-body');
    if (tableBody) {
      tableBody.innerHTML = '';
      if (docs.length === 0) {
        tableBody.innerHTML = `<tr><td colspan="4" style="text-align: center; color: var(--text-muted);">No records cataloged yet.</td></tr>`;
      } else {
        docs.forEach(doc => {
          const sizeKB = (doc.size / 1024).toFixed(1);
          const tr = document.createElement('tr');
          tr.innerHTML = `
            <td><strong style="color:var(--accent-gold);">${doc.name}</strong></td>
            <td>${sizeKB} KB</td>
            <td>${doc.uploadDate}</td>
            <td><span class="doc-badge doc-badge-folder" style="background:rgba(45,212,191,0.1); color:var(--accent-teal);">Analyzed</span></td>
          `;
          tableBody.appendChild(tr);
        });
      }
    }
  }
}

// --- SPECIFIC WORKSPACE INTERACTIVE LOGICS ---

// A. Flashcards flips & cycling
function updateStudyFlashcard() {
  const card = FLASHCARDS[currentFlashcardIndex];
  document.getElementById('flashcard-front-text').textContent = card.q;
  document.getElementById('flashcard-back-text').textContent = card.a;
  document.getElementById('flashcard-index-tracker').textContent = `Card ${currentFlashcardIndex + 1} of ${FLASHCARDS.length}`;
  document.getElementById('flashcard-inner-box').classList.remove('is-flipped');
}

// B. Citation references formulator
function updateResearchCitation() {
  const select = document.getElementById('citation-doc-select');
  const resultBox = document.getElementById('citation-result-box');
  const abstractBox = document.getElementById('research-abstract-preview');
  if (!select || !resultBox) return;

  const docId = select.value;
  if (!docId) return;

  const doc = state.documents.find(d => d.id === docId);
  if (!doc) return;

  const stylePills = document.querySelectorAll('#view-research-space .tag-pill');
  let selectedStyle = 'apa';
  stylePills.forEach(pill => {
    if (pill.classList.contains('active')) {
      if (pill.id === 'btn-cite-mla') selectedStyle = 'mla';
      else if (pill.id === 'btn-cite-chicago') selectedStyle = 'chicago';
    }
  });

  const year = new Date().getFullYear();
  let citationText = '';

  if (selectedStyle === 'apa') {
    citationText = `Balaji, T. & Team. (${year}). Analysis of ${doc.name.replace('.pdf', '')}. *DocMind AI Research Journal*, 14(2), 24-39.`;
  } else if (selectedStyle === 'mla') {
    citationText = `Balaji, T., et al. "Analysis of ${doc.name.replace('.pdf', '')}." *DocMind AI Research*, vol. 14, no. 2, ${year}, pp. 24-39.`;
  } else {
    citationText = `Balaji, T. and Team. "Analysis of ${doc.name.replace('.pdf', '')}." *DocMind AI Research* 14, no. 2 (${year}): 24-39.`;
  }

  resultBox.innerHTML = citationText;
  
  if (doc.summary) {
    const firstSentence = doc.summary.split(/[.!?]/)[0] + '.';
    abstractBox.textContent = `Abstract: "${firstSentence}"`;
  } else {
    abstractBox.textContent = "No abstract generated yet.";
  }
}

// C. Reference Glossary Index lookup
function renderGlossaryTerms(filterLetter = "ALL") {
  const container = document.getElementById('glossary-results-container');
  if (!container) return;
  container.innerHTML = '';

  const filtered = filterLetter === "ALL" 
    ? GLOSSARY_ITEMS 
    : GLOSSARY_ITEMS.filter(item => item.letter === filterLetter);

  if (filtered.length === 0) {
    container.innerHTML = `<p style="font-size:0.85rem; color:var(--text-muted); padding:10px;">No terms found starting with "${filterLetter}".</p>`;
    return;
  }

  filtered.forEach(item => {
    const card = document.createElement('div');
    card.className = 'glossary-item-card';
    card.innerHTML = `
      <h6>${item.term}</h6>
      <p>${item.def}</p>
    `;
    container.appendChild(card);
  });
}

// --- STATS & COUNTS MANAGER ---

function updateStats() {
  const dCount = document.getElementById('stat-docs-count');
  const fCount = document.getElementById('stat-folders-count');
  const tCount = document.getElementById('stat-tags-count');
  const cCount = document.getElementById('stat-consults-count');

  if (dCount) dCount.textContent = state.documents.length;
  if (fCount) fCount.textContent = state.folders.length;
  if (tCount) tCount.textContent = state.tags.length;
  
  const totalChatsCount = Object.values(state.chats).reduce((acc, list) => acc + list.filter(m => m.role === 'user').length, 0);
  if (cCount) cCount.textContent = totalChatsCount || 0;
}

function populateFolderDropdowns() {
  const select = document.getElementById('upload-folder-select');
  if (!select) return;
  select.innerHTML = '<option value="">No Folder (Unassigned)</option>';
  state.folders.forEach(f => {
    const opt = document.createElement('option');
    opt.value = f.id;
    opt.textContent = f.name;
    select.appendChild(opt);
  });
}

function populateTagDropdowns() {
  const select = document.getElementById('upload-tag-select');
  if (!select) return;
  select.innerHTML = '<option value="">No Tag</option>';
  state.tags.forEach(t => {
    const opt = document.createElement('option');
    opt.value = t.name;
    opt.textContent = `#${t.name}`;
    select.appendChild(opt);
  });
}

// --- READER WORKSPACE ---

async function openDocumentInReader(docId) {
  state.activeDocId = docId;
  const doc = state.documents.find(d => d.id === docId);
  if (!doc) return;

  switchView('reader');
  
  document.getElementById('reader-document-title').textContent = doc.name;
  
  const pagesContainer = document.getElementById('reader-scroll-container');
  pagesContainer.innerHTML = '';
  
  doc.textPages.forEach((text, index) => {
    const pageCard = document.createElement('div');
    pageCard.className = 'page-paper-card';
    pageCard.id = `reader-page-${index + 1}`;
    
    const formattedText = text.replace(/\s{2,}/g, ' ').replace(/([.!?])\s+/g, '$1\n\n');
    pageCard.innerHTML = `
      ${formattedText}
      <div class="page-number-indicator">Page ${index + 1} of ${doc.textPages.length}</div>
    `;
    pagesContainer.appendChild(pageCard);
  });

  if (!state.chats[docId]) {
    const storedChat = await dbGet('chats', docId);
    state.chats[docId] = storedChat ? storedChat.messages : [
      { role: 'ai', text: `Greetings Scholar! <span class="cursive-text" style="font-size: 1.15rem; display: inline-block;">DocMind AI</span> is active. I have successfully parsed all **${doc.textPages.length} pages** of this document. Ask me any question, or select a helper query below!`, time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }
    ];
  }

  renderChatMessages();
  renderSummaryTab(doc);
  renderTakeawaysTab(doc);
  renderKeywordsTab(doc);
}

function renderChatMessages() {
  const container = document.getElementById('chat-messages-container');
  if (!container) return;
  container.innerHTML = '';
  
  const messages = state.chats[state.activeDocId] || [];
  messages.forEach(msg => {
    const div = document.createElement('div');
    div.className = `chat-message ${msg.role}`;
    
    let formattedText = msg.text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/^\s*\*\s+(.*?)$/gm, '• $1')
      .replace(/\n/g, '<br>');

    div.innerHTML = `
      <div class="message-bubble">${formattedText}</div>
      <div class="message-meta">${msg.time}</div>
    `;
    container.appendChild(div);
  });
  
  container.scrollTop = container.scrollHeight;
}

function renderSummaryTab(doc) {
  const container = document.getElementById('summary-view-container');
  if (!container) return;
  container.innerHTML = `
    <div class="summary-card">
      <div class="summary-section-title">Overview</div>
      <p style="white-space: pre-wrap; font-size: 0.92rem; line-height: 1.6;">${doc.summary}</p>
    </div>
    
    <div class="summary-card">
      <div class="summary-section-title">Document Facts</div>
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 0.8rem;">
        <div><strong>Name:</strong> ${doc.name}</div>
        <div><strong>Total Pages:</strong> ${doc.textPages.length} pages</div>
        <div><strong>File Size:</strong> ${(doc.size / 1024).toFixed(1)} KB</div>
        <div><strong>Analyzed On:</strong> ${doc.uploadDate}</div>
      </div>
    </div>
  `;
}

function renderTakeawaysTab(doc) {
  const container = document.getElementById('takeaways-view-container');
  if (!container) return;
  container.innerHTML = '';
  
  const list = document.createElement('div');
  list.className = 'takeaways-list';
  
  doc.takeaways.forEach(t => {
    const item = document.createElement('div');
    item.className = 'takeaway-item';
    item.innerHTML = `
      <span class="takeaway-bullet"><i class="fa-solid fa-circle-check"></i></span>
      <p class="takeaway-text">${t}</p>
    `;
    list.appendChild(item);
  });

  container.appendChild(list);
}

function renderKeywordsTab(doc) {
  const container = document.getElementById('keywords-view-container');
  if (!container) return;
  container.innerHTML = '';

  if (doc.keywords.length === 0) {
    container.innerHTML = '<p style="font-size: 0.85rem; color: var(--text-muted);">No keywords extracted.</p>';
    return;
  }

  const fullText = doc.textPages.join(' ').toLowerCase();

  doc.keywords.forEach(keyword => {
    const escapedKeyword = keyword.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
    const regex = new RegExp(`\\b${escapedKeyword}\\b`, 'gi');
    const matches = fullText.match(regex);
    const freq = matches ? matches.length : 0;

    const btn = document.createElement('button');
    btn.className = 'keyword-badge-interactive';
    btn.innerHTML = `
      #${keyword} <span>${freq}x</span>
    `;

    btn.addEventListener('click', () => {
      highlightKeywordInReader(keyword);
    });

    container.appendChild(btn);
  });
}

function highlightKeywordInReader(keyword) {
  const pagesContainer = document.getElementById('reader-scroll-container');
  const doc = state.documents.find(d => d.id === state.activeDocId);
  if (!doc) return;

  const marks = pagesContainer.querySelectorAll('mark');
  marks.forEach(m => {
    const textNode = document.createTextNode(m.textContent);
    m.parentNode.replaceChild(textNode, m);
  });

  let foundPage = -1;
  for (let i = 0; i < doc.textPages.length; i++) {
    if (doc.textPages[i].toLowerCase().includes(keyword.toLowerCase())) {
      foundPage = i + 1;
      break;
    }
  }

  if (foundPage === -1) {
    showToast(`Keyword "${keyword}" not found in current page view.`, 'warning');
    return;
  }

  const pageElement = document.getElementById(`reader-page-${foundPage}`);
  if (!pageElement) return;

  const regex = new RegExp(`(${keyword})`, 'gi');
  const nodes = pageElement.childNodes;
  nodes.forEach(node => {
    if (node.nodeType === Node.TEXT_NODE) {
      const text = node.textContent;
      if (regex.test(text)) {
        const span = document.createElement('span');
        span.innerHTML = text.replace(regex, '<mark>$1</mark>');
        node.parentNode.replaceChild(span, node);
      }
    }
  });

  pageElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
  showToast(`Scrolled to Page ${foundPage} containing "${keyword}"`, 'success');
}

// --- DOCUMENT DELETION ---

async function deleteDocument(docId) {
  const doc = state.documents.find(d => d.id === docId);
  state.documents = state.documents.filter(d => d.id !== docId);
  delete state.chats[docId];
  
  await dbDelete('documents', docId);
  await dbDelete('chats', docId);

  if (state.activeDocId === docId) {
    state.activeDocId = null;
    if (doc && doc.folderId) {
      switchView(doc.folderId);
    } else {
      switchView('dashboard');
    }
  } else {
    // Refresh current view
    if (state.activeView === 'dashboard') {
      renderDashboard();
    } else if (state.activeView.startsWith('f-')) {
      renderSpace(state.activeView);
    }
  }

  showToast('Document deleted successfully', 'success');
  renderSidebar();
  updateStats();
  checkStorageUsage();
}

// --- NAVIGATION ROUTER v4 (Separate Pages Workspace Routing) ---

function switchView(viewName) {
  state.activeView = viewName;
  
  const viewLanding = document.getElementById('view-landing');
  const viewDashboard = document.getElementById('view-dashboard');
  const viewReader = document.getElementById('view-reader');
  
  // Custom Category Spaces
  const spaces = {
    'f-lectures': document.getElementById('view-lectures-space'),
    'f-exam': document.getElementById('view-study-space'),
    'f-research': document.getElementById('view-research-space'),
    'f-syllabus': document.getElementById('view-syllabus-space'),
    'f-records': document.getElementById('view-office-space'),
    'f-reference': document.getElementById('view-reference-space')
  };

  const sidebar = document.getElementById('sidebar');
  const workspace = document.getElementById('main-workspace');

  const navDashboard = document.getElementById('nav-dashboard');
  const navReader = document.getElementById('nav-reader');

  // Clear sidebar active indicators
  document.querySelectorAll('.folder-item-btn').forEach(btn => btn.classList.remove('active'));

  if (viewName === 'landing') {
    viewLanding.classList.add('active');
    sidebar.style.display = 'none';
    workspace.style.display = 'none';
  } else {
    viewLanding.classList.remove('active');
    sidebar.style.display = 'flex';
    workspace.style.display = 'flex';

    // Hide all panels initially
    viewDashboard.classList.remove('active');
    viewReader.classList.remove('active');
    Object.values(spaces).forEach(sp => { if (sp) sp.classList.remove('active'); });

    if (viewName === 'dashboard') {
      viewDashboard.classList.add('active');
      navDashboard.classList.add('active');
      navReader.classList.remove('active');
      if (!state.activeDocId) navReader.disabled = true;
      
      // Update filters for all notes
      state.filters.folderId = null;
      renderDashboard();
    } 
    
    else if (viewName === 'reader') {
      viewReader.classList.add('active');
      navDashboard.classList.remove('active');
      navReader.classList.add('active');
      navReader.disabled = false;
    } 
    
    else if (spaces[viewName]) {
      // It is a specific folder workspace view
      spaces[viewName].classList.add('active');
      navDashboard.classList.remove('active');
      navReader.classList.remove('active');
      
      // Highlight sidebar folder button
      const folderBtn = document.querySelector(`.folder-item-btn[data-id="${viewName}"]`);
      if (folderBtn) folderBtn.classList.add('active');

      state.filters.folderId = viewName;
      renderSpace(viewName);
    }
  }
}

// --- MODAL CONTROLLERS ---

function openModal(modalId) {
  document.getElementById(modalId).classList.add('active');
}

function closeModal(modalId) {
  document.getElementById(modalId).classList.remove('active');
}

// --- EVENT LISTENERS INITIALIZATION ---

function setupEventListeners() {
  // Landing Page workspace launcher CTAs
  document.getElementById('landing-btn-enter-header').addEventListener('click', () => switchView('dashboard'));
  document.getElementById('landing-btn-enter-hero').addEventListener('click', () => switchView('dashboard'));
  document.getElementById('landing-btn-settings').addEventListener('click', () => {
    document.getElementById('gemini-api-key-input').value = state.settings.geminiKey || '';
    openModal('modal-settings');
  });

  // Logo home triggers
  document.querySelectorAll('.logo').forEach(logo => {
    logo.addEventListener('click', (e) => {
      e.preventDefault();
      switchView('landing');
    });
  });

  // Category Cards Click Filters (Route to separate pages)
  document.querySelectorAll('.category-box').forEach(box => {
    box.addEventListener('click', (e) => {
      const folderId = e.currentTarget.getAttribute('data-folder');
      state.filters.folderId = folderId;
      state.filters.tag = null;
      switchView(folderId);
      renderSidebar();
      showToast(`Welcome to Category Workspace`, 'success');
    });
  });

  // Back to Landing Page navigation
  document.getElementById('btn-back-to-landing').addEventListener('click', () => switchView('landing'));

  // Dashboard buttons
  document.getElementById('nav-dashboard').addEventListener('click', () => switchView('dashboard'));
  document.getElementById('nav-reader').addEventListener('click', () => {
    if (state.activeDocId) switchView('reader');
  });
  document.getElementById('reader-btn-back').addEventListener('click', () => {
    const doc = state.documents.find(d => d.id === state.activeDocId);
    if (doc && doc.folderId) {
      switchView(doc.folderId);
    } else {
      switchView('dashboard');
    }
  });
  
  document.getElementById('sidebar-logo-link').addEventListener('click', (e) => {
    e.preventDefault();
    switchView('landing');
  });

  document.getElementById('mobile-sidebar-toggle').addEventListener('click', () => {
    document.getElementById('sidebar').classList.toggle('open');
  });

  document.getElementById('search-input').addEventListener('input', (e) => {
    state.filters.search = e.target.value;
    if (state.activeView === 'dashboard') {
      renderDashboard();
    } else if (state.activeView.startsWith('f-')) {
      renderSpace(state.activeView);
    }
  });

  document.getElementById('clear-filter-btn').addEventListener('click', () => {
    state.filters.folderId = null;
    state.filters.tag = null;
    state.filters.search = '';
    document.getElementById('search-input').value = '';
    document.querySelectorAll('.tag-pill').forEach(p => p.classList.remove('active'));
    switchView('dashboard');
    renderSidebar();
  });

  // Main Dashboard File Upload dragover & drop
  setupUploadZone('upload-zone', 'file-input', null);
  
  // 6 Custom Category Workspace Upload Zones
  setupUploadZone('upload-zone-lectures', 'file-input-lectures', 'f-lectures');
  setupUploadZone('upload-zone-study', 'file-input-study', 'f-exam');
  setupUploadZone('upload-zone-research', 'file-input-research', 'f-research');
  setupUploadZone('upload-zone-syllabus', 'file-input-syllabus', 'f-syllabus');
  setupUploadZone('upload-zone-office', 'file-input-office', 'f-records');
  setupUploadZone('upload-zone-reference', 'file-input-reference', 'f-reference');

  // Modals Buttons
  document.getElementById('btn-add-folder-modal').addEventListener('click', () => openModal('modal-folder'));
  document.getElementById('btn-add-tag-modal').addEventListener('click', () => openModal('modal-tag'));
  document.getElementById('btn-settings-modal').addEventListener('click', () => {
    document.getElementById('gemini-api-key-input').value = state.settings.geminiKey || '';
    openModal('modal-settings');
  });

  document.querySelectorAll('.modal-close').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const modal = e.target.closest('.modal-overlay');
      if (modal) modal.classList.remove('active');
    });
  });

  // Theme Switches
  document.getElementById('btn-theme-toggle').addEventListener('click', () => {
    const newTheme = state.settings.theme === 'dark' ? 'light' : 'dark';
    state.settings.theme = newTheme;
    dbSave('settings', { key: 'theme', value: newTheme });
    applyTheme(newTheme);
  });

  // Create Folder
  document.getElementById('btn-save-folder').addEventListener('click', async () => {
    const input = document.getElementById('folder-name-input');
    const name = input.value.trim();
    if (!name) return showToast('Please enter a folder name', 'warning');

    const selectedColorOption = document.querySelector('.color-option.selected');
    const color = selectedColorOption ? selectedColorOption.getAttribute('data-color') : FOLDER_COLORS[0];
    
    const folderId = 'folder-' + Date.now();
    const newFolder = { id: folderId, name, color };

    state.folders.push(newFolder);
    await dbSave('folders', newFolder);
    
    input.value = '';
    closeModal('modal-folder');
    showToast(`Folder "${name}" created`, 'success');
    
    populateFolderDropdowns();
    renderSidebar();
    updateStats();
  });

  document.querySelectorAll('.color-option').forEach(opt => {
    opt.addEventListener('click', (e) => {
      document.querySelectorAll('.color-option').forEach(o => o.classList.remove('selected'));
      e.target.classList.add('selected');
    });
  });

  // Create Tag
  document.getElementById('btn-save-tag').addEventListener('click', async () => {
    const input = document.getElementById('tag-name-input');
    const name = input.value.trim().replace(/[^a-zA-Z0-9-]/g, '');
    if (!name) return showToast('Please enter a valid tag name (letters, numbers, dashes)', 'warning');

    if (state.tags.some(t => t.name.toLowerCase() === name.toLowerCase())) {
      return showToast('Tag already exists', 'warning');
    }

    const newTag = { name };
    state.tags.push(newTag);
    await dbSave('tags', newTag);

    input.value = '';
    closeModal('modal-tag');
    showToast(`Tag #${name} created`, 'success');

    populateTagDropdowns();
    renderSidebar();
    updateStats();
  });

  // Settings saves
  document.getElementById('btn-save-settings').addEventListener('click', async () => {
    const key = document.getElementById('gemini-api-key-input').value.trim();
    state.settings.geminiKey = key;
    await dbSave('settings', { key: 'geminiKey', value: key });
    
    closeModal('modal-settings');
    updateApiStatusBadge();
    showToast('Settings saved successfully', 'success');
  });

  // Database wipe operations
  document.getElementById('btn-clear-all-data').addEventListener('click', async () => {
    if (confirm('CAUTION: This will permanently wipe all documents, chat logs, tags, and settings. Proceed?')) {
      const req = indexedDB.deleteDatabase(DB_NAME);
      req.onsuccess = () => {
        showToast('All browser data wiped. Reloading page...', 'info');
        setTimeout(() => location.reload(), 1500);
      };
      req.onerror = () => showToast('Failed to clear database', 'danger');
    }
  });

  document.getElementById('btn-toggle-key-visibility').addEventListener('click', () => {
    const input = document.getElementById('gemini-api-key-input');
    const icon = document.querySelector('#btn-toggle-key-visibility i');
    if (input.type === 'password') {
      input.type = 'text';
      icon.className = 'fa-solid fa-eye-slash';
    } else {
      input.type = 'password';
      icon.className = 'fa-solid fa-eye';
    }
  });

  // Tab views switching
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const activeTab = e.currentTarget.getAttribute('data-tab');
      
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      e.currentTarget.classList.add('active');

      document.querySelectorAll('.tab-pane-content').forEach(p => p.classList.remove('active'));
      document.getElementById(activeTab).classList.add('active');
    });
  });

  // Chat forms submitters
  document.getElementById('btn-chat-send').addEventListener('click', handleChatSubmit);
  document.getElementById('chat-input').addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleChatSubmit();
    }
  });

  document.querySelectorAll('.suggestion-pill').forEach(pill => {
    pill.addEventListener('click', (e) => {
      document.getElementById('chat-input').value = e.target.textContent;
      handleChatSubmit();
    });
  });

  // Flashcards flippers
  const flipper = document.getElementById('btn-flashcard-flip');
  if (flipper) {
    flipper.addEventListener('click', () => {
      document.getElementById('flashcard-inner-box').classList.toggle('is-flipped');
    });
  }

  // Flashcards cycle
  document.getElementById('btn-flashcard-prev').addEventListener('click', () => {
    currentFlashcardIndex = (currentFlashcardIndex - 1 + FLASHCARDS.length) % FLASHCARDS.length;
    updateStudyFlashcard();
  });
  document.getElementById('btn-flashcard-next').addEventListener('click', () => {
    currentFlashcardIndex = (currentFlashcardIndex + 1) % FLASHCARDS.length;
    updateStudyFlashcard();
  });

  // Citation select & triggers
  const citationSelect = document.getElementById('citation-doc-select');
  if (citationSelect) {
    citationSelect.addEventListener('change', updateResearchCitation);
  }
  document.getElementById('btn-cite-apa').addEventListener('click', (e) => {
    highlightCitationPill(e.target);
    updateResearchCitation();
  });
  document.getElementById('btn-cite-mla').addEventListener('click', (e) => {
    highlightCitationPill(e.target);
    updateResearchCitation();
  });
  document.getElementById('btn-cite-chicago').addEventListener('click', (e) => {
    highlightCitationPill(e.target);
    updateResearchCitation();
  });

  // Reference Glossary filters
  document.querySelectorAll('.alphabet-pill').forEach(pill => {
    pill.addEventListener('click', (e) => {
      document.querySelectorAll('.alphabet-pill').forEach(p => p.classList.remove('active'));
      e.target.classList.add('active');
      const letter = e.target.getAttribute('data-letter');
      renderGlossaryTerms(letter);
    });
  });
}

function highlightCitationPill(target) {
  const pills = document.querySelectorAll('#view-research-space .tag-pill');
  pills.forEach(p => p.classList.remove('active'));
  target.classList.add('active');
}

// Helper: Configure upload elements inside specific containers
function setupUploadZone(zoneId, inputId, defaultFolderId) {
  const zone = document.getElementById(zoneId);
  const input = document.getElementById(inputId);
  if (!zone || !input) return;

  zone.addEventListener('click', () => input.click());

  zone.addEventListener('dragover', (e) => {
    e.preventDefault();
    zone.style.borderColor = 'var(--accent-gold)';
    zone.style.background = 'rgba(245, 208, 97, 0.04)';
  });

  zone.addEventListener('dragleave', () => {
    zone.style.borderColor = 'var(--border-color)';
    zone.style.background = 'none';
  });

  zone.addEventListener('drop', async (e) => {
    e.preventDefault();
    zone.style.borderColor = 'var(--border-color)';
    zone.style.background = 'none';
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFilesUpload(files, defaultFolderId);
    }
  });

  input.addEventListener('change', (e) => {
    const files = e.target.files;
    if (files.length > 0) {
      handleFilesUpload(files, defaultFolderId);
    }
  });
}

// --- FILE UPLOADS DISPATCHER ---

async function handleFilesUpload(files, folderId = null) {
  const selectedTag = document.getElementById('upload-tag-select')?.value || null;

  for (let i = 0; i < files.length; i++) {
    const file = files[i];
    if (file.type !== 'application/pdf') {
      showToast(`${file.name} is not a PDF file.`, 'warning');
      continue;
    }
    
    if (file.size > 15 * 1024 * 1024) {
      showToast(`${file.name} exceeds 15MB file size limit.`, 'warning');
      continue;
    }

    await parseAndRegisterPDF(file, folderId, selectedTag);
  }
}

// --- CHAT FORM CONTROLLER ---

async function handleChatSubmit() {
  const input = document.getElementById('chat-input');
  const query = input.value.trim();
  if (!query) return;

  const docId = state.activeDocId;
  const doc = state.documents.find(d => d.id === docId);
  if (!doc) return;

  const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  const userMessage = { role: 'user', text: query, time };
  
  state.chats[docId].push(userMessage);
  renderChatMessages();
  input.value = '';

  const aiLoadingMessage = { role: 'ai', text: '<span class="scanning-text">Thinking...</span>', time: 'Just now' };
  state.chats[docId].push(aiLoadingMessage);
  renderChatMessages();

  try {
    const answer = await answerQuestionAboutDocument(doc, query);
    
    state.chats[docId].pop();
    
    const realAiMsg = {
      role: 'ai',
      text: answer,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    
    state.chats[docId].push(realAiMsg);
    await dbSave('chats', { docId, messages: state.chats[docId] });
    
    renderChatMessages();
    updateStats();
  } catch (error) {
    console.error('Chat AI failure:', error);
    state.chats[docId].pop();
    state.chats[docId].push({
      role: 'ai',
      text: `Error during consult: ${error.message}.`,
      time: 'Just now'
    });
    renderChatMessages();
  }
}

// --- TOAST SYSTEMS ---

function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;
  const toast = document.createElement('div');
  toast.className = 'custom-toast';
  
  let borderLeftColor = 'var(--accent-teal)';
  let icon = '<i class="fa-solid fa-circle-info"></i>';

  if (type === 'success') {
    borderLeftColor = 'var(--success)';
    icon = '<i class="fa-solid fa-circle-check" style="color: var(--success);"></i>';
  } else if (type === 'warning') {
    borderLeftColor = 'var(--warning)';
    icon = '<i class="fa-solid fa-circle-exclamation" style="color: var(--warning);"></i>';
  } else if (type === 'danger') {
    borderLeftColor = 'var(--danger)';
    icon = '<i class="fa-solid fa-triangle-exclamation" style="color: var(--danger);"></i>';
  }

  toast.style.borderLeftColor = borderLeftColor;
  toast.innerHTML = `${icon} <span>${message}</span>`;
  
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.animation = 'toast-slide-in 0.3s ease reverse forwards';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}
