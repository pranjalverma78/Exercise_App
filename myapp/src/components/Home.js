// src/components/Home.js
import React from 'react';
import { Link } from 'react-router-dom';

function Home() {
  return (
    <div style={{ textAlign: 'center', marginTop: '50px' }}>
      <h1>Welcome to the Push-Up Counter</h1>
      <Link to="/counter">
        <button style={{ padding: '10px 20px', fontSize: '16px' }}>Push-Up</button>
      </Link>
    </div>
  );
}

export default Home;
