import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-app.js";
import { getAuth, GoogleAuthProvider, signInWithPopup, onAuthStateChanged, signOut } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-auth.js";
import { firebaseConfig } from "../shared/firebase-config.js";

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const provider = new GoogleAuthProvider();

export async function signIn() {
  const result = await signInWithPopup(auth, provider);
  return result.user.getIdToken();
}

export function onAuthChanged(callback) {
  onAuthStateChanged(auth, callback);
}

export async function getIdToken() {
  const user = auth.currentUser;
  return user ? user.getIdToken(true) : null;
}

export async function doSignOut() {
  await signOut(auth);
}

export function currentUser() {
  return auth.currentUser;
}
