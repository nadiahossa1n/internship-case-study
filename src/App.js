import React, { useState } from "react";
import "./App.css";
import ChatWindow from "./components/ChatWindow";

function App() {

  return (
    <div className="App">
      <div className="heading">
        Bao Distributors
      </div>
        <ChatWindow/>
    </div>
  );
}

export default App;
