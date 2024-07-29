import { initializeApp } from 'https://www.gstatic.com/firebasejs/10.8.0/firebase-app.js';
import {
	getAuth,
	signInWithEmailAndPassword,
} from 'https://www.gstatic.com/firebasejs/10.8.0/firebase-auth.js';

var firebaseConfig = {
	apiKey: 'AIzaSyCvvDkM85fj8BMWJ9i0JFgoQVL2cDaYUZ4',
	authDomain: 'msgbot-293d3.firebaseapp.com',
	databaseURL: 'https://msgbot-293d3.firebaseio.com',
	projectId: 'msgbot-293d3',
	storageBucket: 'msgbot-293d3.appspot.com',
	messagingSenderId: '586817029821',
	appId: '1:586817029821:web:68f414134931710a4319d4',
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

function showMessage(message, type) {
	var showElement = document.getElementById('show-message');
	showElement.innerHTML = message;
	showElement.classList.remove('alert-success', 'alert-danger', 'd-none');
	showElement.classList.add('alert-' + type);
}

document.getElementById('sign-in-button').addEventListener('click', async (e) => {
	const email = document.getElementById('sign-in-email').value;
	const password = document.getElementById('sign-in-password').value;

	if (email && password) {
		e.currentTarget?.setAttribute('disabled', true);
		try {
			const userCredential = await signInWithEmailAndPassword(auth, email, password);
			const user = userCredential?.user;
			if (user) {
				const response = await fetch('/sign-in', {
					method: 'POST',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify(user),
				});
				const data = await response.json();
				data.success && (window.location.href = '/');
				data.error && showMessage(data.error, 'danger');
			}
		} catch (err) {
			showMessage(err?.message, 'danger');
		} finally {
			e.currentTarget?.removeAttribute('disabled');
		}
	} else showMessage('Please enter both email and password.', 'danger');
});
