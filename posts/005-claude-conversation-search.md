---
title: "Search Your Claude Conversations by Content"
date: 2025-11-26
tags: [tools, productivity, claude, search]
---

# Search Your Claude Conversations by Content

One limitation of Claude.ai's interface is that you can only search conversations by title, not by their actual content. If you've had hundreds of conversations and want to find that specific discussion about, say, "recursive algorithms" or "sourdough starter troubleshooting," you're out of luck with the built-in search.

Until now.

## The Solution: A Local Conversation Browser

I've built a simple tool that lets you search through your exported Claude conversations by their actual content. Here's what makes it useful:

- **Content Search**: Find conversations containing specific text, not just titles
- **Case-Insensitive**: Searches work regardless of capitalization
- **Complete Privacy**: All processing happens in your browser - no data leaves your machine
- **Simple Interface**: Upload, search, click to open conversations

## Privacy First

This tool processes your conversation data entirely within your browser. Nothing is uploaded to any server. You can verify this by opening your browser's Developer Tools (F12), going to the Network tab, and uploading a file - you'll see no network requests are made.

## How to Use It

1. Export your conversations from Claude.ai (Settings → Data Export)
2. Upload the JSON file using the tool below
3. Search for any text that appeared in your conversations
4. Click conversation titles to open them directly in Claude.ai

## The Tool

<div style="border: 2px solid #ddd; border-radius: 8px; padding: 20px; margin: 20px 0;">

<style>
.conv-browser {
    font-family: Arial, sans-serif;
    max-width: 100%;
    background-color: #f9f9f9;
    padding: 15px;
    border-radius: 6px;
}

.conv-privacy-notice {
    background-color: #e8f5e8;
    border: 1px solid #4caf50;
    border-radius: 4px;
    padding: 12px;
    margin-bottom: 15px;
}

.conv-privacy-notice h4 {
    margin: 0 0 8px 0;
    color: #2e7d32;
    font-size: 14px;
}

.conv-privacy-notice p {
    margin: 3px 0;
    color: #388e3c;
    font-size: 12px;
}

.conv-upload-section {
    margin-bottom: 20px;
    padding: 15px;
    border: 2px dashed #ccc;
    border-radius: 6px;
    text-align: center;
    background: white;
}

.conv-upload-button {
    background-color: #007acc;
    color: white;
    padding: 8px 16px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
}

.conv-upload-button:hover {
    background-color: #005999;
}

.conv-search-section {
    margin-bottom: 15px;
    padding: 12px;
    background-color: #f8f9fa;
    border-radius: 4px;
}

.conv-search-input {
    width: 250px;
    padding: 6px;
    border: 1px solid #ccc;
    border-radius: 4px;
    margin-right: 8px;
    font-size: 14px;
}

.conv-search-button {
    padding: 6px 12px;
    background-color: #28a745;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
}

.conv-clear-button {
    padding: 6px 12px;
    background-color: #6c757d;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    margin-left: 4px;
    font-size: 14px;
}

.conv-conversation-item {
    border: 1px solid #ddd;
    border-radius: 4px;
    margin-bottom: 8px;
    padding: 12px;
    background-color: white;
    font-size: 14px;
}

.conv-conversation-title {
    font-weight: bold;
    margin-bottom: 4px;
}

.conv-conversation-title a {
    color: #007acc;
    text-decoration: none;
}

.conv-conversation-title a:hover {
    text-decoration: underline;
}

.conv-conversation-meta {
    color: #666;
    font-size: 11px;
    margin-bottom: 6px;
}

.conv-conversation-preview {
    color: #333;
    font-size: 12px;
    max-height: 50px;
    overflow: hidden;
    line-height: 1.3;
}

.conv-pagination {
    text-align: center;
    margin-top: 15px;
}

.conv-pagination button {
    padding: 6px 10px;
    margin: 0 2px;
    border: 1px solid #ddd;
    background-color: #fff;
    cursor: pointer;
    border-radius: 3px;
    font-size: 12px;
}

.conv-pagination button:hover {
    background-color: #f8f9fa;
}

.conv-pagination button.active {
    background-color: #007acc;
    color: white;
    border-color: #007acc;
}

.conv-pagination button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.conv-stats {
    background-color: #e9ecef;
    padding: 8px;
    border-radius: 4px;
    margin-bottom: 15px;
    font-size: 12px;
}

.conv-hidden {
    display: none;
}

.conv-error {
    background-color: #f8d7da;
    color: #721c24;
    padding: 12px;
    border-radius: 4px;
    margin-bottom: 15px;
    font-size: 14px;
}
</style>

<div class="conv-browser">
    <div class="conv-privacy-notice">
        <h4>🔒 Your Privacy is Protected</h4>
        <p><strong>All data stays in your browser.</strong> This tool processes your conversation export locally - nothing is uploaded to any server.</p>
        <p><strong>Want to verify?</strong> Open your browser's Developer Tools (F12) → Network tab, then upload a file. You'll see no network requests are made.</p>
    </div>
    
    <div class="conv-upload-section" id="convUploadSection">
        <p style="margin: 0 0 10px 0;">Upload your exported Claude conversations JSON file</p>
        <input type="file" id="convFileInput" accept=".json" style="display: none;">
        <button class="conv-upload-button" onclick="document.getElementById('convFileInput').click()">
            Choose JSON File
        </button>
    </div>
    
    <div id="convErrorMessage" class="conv-error conv-hidden"></div>
    
    <div id="convMainContent" class="conv-hidden">
        <div class="conv-search-section">
            <input type="text" id="convSearchInput" class="conv-search-input" placeholder="Search conversations and messages...">
            <button class="conv-search-button" onclick="convPerformSearch()">Search</button>
            <button class="conv-clear-button" onclick="convClearSearch()">Clear</button>
        </div>
        
        <div id="convStatsSection" class="conv-stats"></div>
        
        <div id="convConversationList"></div>
        
        <div id="convPagination" class="conv-pagination"></div>
    </div>
</div>

<script>
// Conversation browser functionality
(function() {
    let convAllConversations = [];
    let convFilteredConversations = [];
    let convCurrentPage = 1;
    const convItemsPerPage = 8;
    let convCurrentSearchTerm = '';

    document.getElementById('convFileInput').addEventListener('change', convHandleFileUpload);

    function convHandleFileUpload(event) {
        const file = event.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = function(e) {
            try {
                const jsonData = JSON.parse(e.target.result);
                if (Array.isArray(jsonData)) {
                    convAllConversations = jsonData;
                    convFilteredConversations = [...convAllConversations];
                    convCurrentPage = 1;
                    convCurrentSearchTerm = '';
                    document.getElementById('convSearchInput').value = '';
                    convShowMainContent();
                    convUpdateDisplay();
                } else {
                    convShowError('Invalid JSON format. Expected an array of conversations.');
                }
            } catch (error) {
                convShowError('Error parsing JSON file: ' + error.message);
            }
        };
        reader.readAsText(file);
    }

    function convShowError(message) {
        document.getElementById('convErrorMessage').textContent = message;
        document.getElementById('convErrorMessage').classList.remove('conv-hidden');
        document.getElementById('convMainContent').classList.add('conv-hidden');
    }

    function convShowMainContent() {
        document.getElementById('convErrorMessage').classList.add('conv-hidden');
        document.getElementById('convMainContent').classList.remove('conv-hidden');
    }

    window.convPerformSearch = function() {
        const searchTerm = document.getElementById('convSearchInput').value;
        convCurrentSearchTerm = searchTerm;
        convCurrentPage = 1;
        
        if (!searchTerm.trim()) {
            convFilteredConversations = [...convAllConversations];
        } else {
            const lowerSearchTerm = searchTerm.toLowerCase();
            
            convFilteredConversations = convAllConversations.filter(conversation => {
                if (conversation.name && conversation.name.toLowerCase().includes(lowerSearchTerm)) {
                    return true;
                }
                
                if (conversation.summary && conversation.summary.toLowerCase().includes(lowerSearchTerm)) {
                    return true;
                }
                
                if (conversation.chat_messages) {
                    return conversation.chat_messages.some(message => 
                        message.text && message.text.toLowerCase().includes(lowerSearchTerm)
                    );
                }
                
                return false;
            });
        }
        
        convUpdateDisplay();
    }

    window.convClearSearch = function() {
        document.getElementById('convSearchInput').value = '';
        convCurrentSearchTerm = '';
        convCurrentPage = 1;
        convFilteredConversations = [...convAllConversations];
        convUpdateDisplay();
    }

    function convUpdateDisplay() {
        convUpdateStats();
        convUpdateConversationList();
        convUpdatePagination();
    }

    function convUpdateStats() {
        const total = convAllConversations.length;
        const filtered = convFilteredConversations.length;
        const searchText = convCurrentSearchTerm ? ` (filtered by "${convCurrentSearchTerm}")` : '';
        
        document.getElementById('convStatsSection').innerHTML = 
            `Showing ${filtered} of ${total} conversations${searchText}`;
    }

    function convUpdateConversationList() {
        const startIndex = (convCurrentPage - 1) * convItemsPerPage;
        const endIndex = startIndex + convItemsPerPage;
        const pageConversations = convFilteredConversations.slice(startIndex, endIndex);
        
        const listHTML = pageConversations.map(conversation => {
            const title = conversation.name || 'Untitled Conversation';
            const createdDate = new Date(conversation.created_at).toLocaleDateString();
            const messageCount = conversation.chat_messages ? conversation.chat_messages.length : 0;
            
            let preview = '';
            if (conversation.chat_messages && conversation.chat_messages.length > 0) {
                const firstMessage = conversation.chat_messages[0];
                preview = firstMessage.text ? firstMessage.text.substring(0, 150) + '...' : '';
            }
            
            const link = `https://claude.ai/chat/${conversation.uuid}`;
            
            return `
                <div class="conv-conversation-item">
                    <div class="conv-conversation-title">
                        <a href="${link}" target="_blank">${convEscapeHtml(title)}</a>
                    </div>
                    <div class="conv-conversation-meta">
                        ${createdDate} | ${messageCount} messages
                    </div>
                    <div class="conv-conversation-preview">
                        ${convEscapeHtml(preview)}
                    </div>
                </div>
            `;
        }).join('');
        
        document.getElementById('convConversationList').innerHTML = listHTML;
    }

    function convUpdatePagination() {
        const totalPages = Math.ceil(convFilteredConversations.length / convItemsPerPage);
        
        if (totalPages <= 1) {
            document.getElementById('convPagination').innerHTML = '';
            return;
        }
        
        let paginationHTML = '';
        
        paginationHTML += `<button onclick="convChangePage(${convCurrentPage - 1})" ${convCurrentPage === 1 ? 'disabled' : ''}>Previous</button>`;
        
        for (let i = 1; i <= totalPages; i++) {
            if (i === 1 || i === totalPages || (i >= convCurrentPage - 2 && i <= convCurrentPage + 2)) {
                paginationHTML += `<button onclick="convChangePage(${i})" ${i === convCurrentPage ? 'class="active"' : ''}>${i}</button>`;
            } else if (i === convCurrentPage - 3 || i === convCurrentPage + 3) {
                paginationHTML += '<span>...</span>';
            }
        }
        
        paginationHTML += `<button onclick="convChangePage(${convCurrentPage + 1})" ${convCurrentPage === totalPages ? 'disabled' : ''}>Next</button>`;
        
        document.getElementById('convPagination').innerHTML = paginationHTML;
    }

    window.convChangePage = function(page) {
        const totalPages = Math.ceil(convFilteredConversations.length / convItemsPerPage);
        if (page >= 1 && page <= totalPages) {
            convCurrentPage = page;
            convUpdateDisplay();
        }
    }

    function convEscapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    document.getElementById('convSearchInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            convPerformSearch();
        }
    });
})();
</script>

</div>

## How It Works

The tool is built as a simple HTML page with JavaScript that:

1. **Parses your JSON export locally** using the browser's FileReader API
2. **Filters conversations** based on case-insensitive text matching across titles, summaries, and message content
3. **Displays results** with pagination and direct links back to Claude.ai
4. **Makes no network requests** - everything happens in your browser's memory

The code is intentionally simple and transparent so you can verify exactly what it's doing. No minification, no obfuscation, just straightforward JavaScript.

## Why This Matters

As we have more conversations with AI systems, finding specific past discussions becomes increasingly important. Whether you're:

- Looking for that coding solution you discussed weeks ago
- Finding research insights from a previous conversation
- Locating specific advice or explanations you received

Content search transforms your conversation history from a linear timeline into a searchable knowledge base.

## Technical Notes

The tool expects Claude's standard export format: a JSON array of conversation objects with `uuid`, `name`, `summary`, `chat_messages`, and other metadata. It handles conversations without titles and gracefully deals with missing or malformed data.

Search is performed using JavaScript's `includes()` method on lowercased strings - simple but effective for most use cases. The pagination keeps performance smooth even with large conversation exports.

---

*Want the standalone version? The complete tool is available as a single HTML file that you can save and use offline.*
