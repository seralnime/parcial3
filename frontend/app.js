const API_URL = 'http://localhost:8000';
let token = localStorage.getItem('token');
let currentRoomId = null;
let ws = null;
let currentUser = null;

// Init
if (token) {
    showChat();
    fetchRooms();
    // Decode token to get username (simple decode, not verify)
    const payload = JSON.parse(atob(token.split('.')[1]));
    currentUser = payload.sub;
}

async function register() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    try {
        const response = await fetch(`${API_URL}/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        if (response.ok) {
            alert('Registered successfully! Please login.');
        } else {
            const data = await response.json();
            alert(data.detail);
        }
    } catch (e) {
        console.error(e);
        alert('Error registering');
    }
}

async function login() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    try {
        const response = await fetch(`${API_URL}/token`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData
        });
        
        if (response.ok) {
            const data = await response.json();
            token = data.access_token;
            localStorage.setItem('token', token);
            currentUser = username;
            showChat();
            fetchRooms();
        } else {
            alert('Invalid credentials');
        }
    } catch (e) {
        console.error(e);
        alert('Error logging in');
    }
}

function logout() {
    localStorage.removeItem('token');
    token = null;
    currentUser = null;
    if (ws) ws.close();
    document.getElementById('auth-section').style.display = 'flex';
    document.getElementById('chat-section').style.display = 'none';
}

function showChat() {
    document.getElementById('auth-section').style.display = 'none';
    document.getElementById('chat-section').style.display = 'flex';
}

async function fetchRooms() {
    const response = await fetch(`${API_URL}/rooms/`, {
        headers: { 'Authorization': `Bearer ${token}` }
    });
    const rooms = await response.json();
    const list = document.getElementById('room-list');
    list.innerHTML = '';
    rooms.forEach(room => {
        const div = document.createElement('div');
        div.className = `room-item ${currentRoomId === room.id ? 'active' : ''}`;
        div.innerText = room.name;
        div.onclick = () => joinRoom(room.id, room.name);
        list.appendChild(div);
    });
}

async function createRoom() {
    const name = document.getElementById('new-room-name').value;
    if (!name) return;

    await fetch(`${API_URL}/rooms/`, {
        method: 'POST',
        headers: { 
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ name })
    });
    document.getElementById('new-room-name').value = '';
    fetchRooms();
}

async function joinRoom(roomId, roomName) {
    if (currentRoomId === roomId) return;
    currentRoomId = roomId;
    document.getElementById('current-room-name').innerText = roomName;
    document.getElementById('chat-messages').innerHTML = '';
    
    // Highlight active room
    fetchRooms(); // Re-render to update active class

    // Load History
    const response = await fetch(`${API_URL}/history/${roomId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
    });
    const history = await response.json();
    history.forEach(msg => appendMessage(msg));

    // Connect WebSocket
    if (ws) ws.close();
    ws = new WebSocket(`ws://localhost:8000/ws/${roomId}/${token}`);
    
    ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        appendMessage(msg);
    };
}

function appendMessage(msg) {
    const div = document.createElement('div');
    const isMe = msg.username === currentUser;
    div.className = `message ${isMe ? 'my-message' : 'other-message'}`;
    
    const userDiv = document.createElement('div');
    userDiv.className = 'message-username';
    userDiv.innerText = msg.username;
    
    const contentDiv = document.createElement('div');
    contentDiv.innerText = msg.content;
    
    div.appendChild(userDiv);
    div.appendChild(contentDiv);
    
    const container = document.getElementById('chat-messages');
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

function sendMessage() {
    const input = document.getElementById('message-input');
    const content = input.value;
    if (!content || !ws) return;
    
    ws.send(JSON.stringify({ content }));
    input.value = '';
}

// Allow Enter key to send
document.getElementById('message-input').addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});
