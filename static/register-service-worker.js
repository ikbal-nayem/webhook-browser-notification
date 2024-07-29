'use strict';

function urlB64ToUint8Array(base64String) {
	const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
	const base64 = (base64String + padding).replace(/\-/g, '+').replace(/_/g, '/');

	const rawData = window.atob(base64);
	const outputArray = new Uint8Array(rawData.length);
	for (let i = 0; i < rawData.length; ++i) {
		outputArray[i] = rawData.charCodeAt(i);
	}
	return outputArray;
}

function updateSubscriptionOnServer(subscription, apiEndpoint, user) {
	return fetch(apiEndpoint, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({
			subscription_json: JSON.stringify(subscription),
			user: user,
		}),
	});
}

function subscribeUser(swRegistration, applicationServerPublicKey, apiEndpoint, user) {
	const applicationServerKey = urlB64ToUint8Array(applicationServerPublicKey);
	swRegistration.pushManager
		.subscribe({
			userVisibleOnly: true,
			applicationServerKey: applicationServerKey,
		})
		.then(function (subscription) {
			console.log(user, ' is subscribed.');
			return updateSubscriptionOnServer(subscription, apiEndpoint, user);
		})
		.then(function (response) {
			if (!response.ok) {
				throw new Error('Bad status code from server.');
			}
			return response.json();
		})
		.then(function (responseData) {
			console.log(responseData);
			if (responseData.status !== 'success') {
				throw new Error('Bad response from server.');
			}
		})
		.catch(function (err) {
			console.log('Failed to subscribe the user: ', err);
			console.log(err.stack);
		});
}

function registerServiceWorker(serviceWorkerUrl, applicationServerPublicKey, apiEndpoint, user) {
	let swRegistration = null;
	if ('serviceWorker' in navigator && 'PushManager' in window) {
		navigator.serviceWorker
			.register(serviceWorkerUrl)
			.then(function (swReg) {
				swRegistration = swReg;
				setTimeout(() => subscribeUser(swRegistration, applicationServerPublicKey, apiEndpoint, user), 2000);
			})
			.catch(function (error) {
				console.error('Service Worker Error', error);
			});
	} else {
		alert('Push messaging is not supported');
	}
	return swRegistration;
}
