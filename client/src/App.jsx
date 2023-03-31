import React, { useState, useEffect } from 'react';

import ImageRanker  from './image/ImageRanker';
import ImageViewer from './image/imageViewer'
import axios from 'axios';

import './App.css'

const serverAddress = 'http://192.168.1.152:3333'

function App() {
  const [imageViewerVisibility, setImageViewerVisibility] = useState(false);
  const [imageRankerVisibility, setImageRankerVisibility] = useState(true);

  const switchToImageViewer = () =>{
    setImageViewerVisibility(true);
    setImageRankerVisibility(false);}

  const switchToImageRanker = () =>{
    setImageViewerVisibility(false);
    setImageRankerVisibility(true);}


  const [user, setUser] = useState(false);
  const [currentFolder, setCurrentFolder] = useState('');
  const [availableFolders, setAvailableFolders] = useState([]);

  const get_folder = () => {
    var query = `${serverAddress}/get_folder/${user}`
    axios.get(query).then((response) => {
      setCurrentFolder(response.data);
    });
  }

  const process_user = (user) =>{
    setUser(user)
    get_folder();
  }

  const handle_username = (e) => {
    if (e.key === 'Enter') {
      process_user(e.target.value)
    }
  }

  function available_folders(){
    var query = `${serverAddress}/available_folders/${user}`
    axios.get(query).then((response) => {
      setAvailableFolders(response.data);
    });
  }

  const set_folder = (folder) => {
    setCurrentFolder(folder);
    var query = `${serverAddress}/set_folder/${user}/folder`
    axios.get(query).then((response) => {
      console.log('good');
    });
  }

  useEffect(() => {
    available_folders();
  }, []);

  return (
    <div>
      {!user && <div id="registration_form">
        <input 
            type="text"
            placeholder="login"
            onKeyDown={(e) => handle_username(e)}
            id="username"
        />
      </div>}

      {false && user && <select id="folder"
        onChange={(e) => {set_folder(e.target.value)}}
        value={currentFolder}>
          
          {availableFolders.map((folder, index) => 
            <option value={folder}
            key={index}
            className="folder_option"
            >{folder}</option>
          )}
      </select>}

      <div id="menu_container">
        <button onClick={() => switchToImageRanker()} className="menu_option">image ranker</button><br/>
        <button onClick={() => switchToImageViewer()} className="menu_option">view images</button><br/>
      </div>

      <div style={{textAlign: 'center', position:'absolute', bottom: '10%', left: '50%', transform: 'translate(-50%)', minWidth: '80%'}}>
        {user && imageRankerVisibility && 
              <ImageRanker props={{'user': user, 'serverAddress': serverAddress}}/>}
      </div>
      
      {imageViewerVisibility && 
      <ImageViewer props={{'thumbnail_dir': currentFolder + '_th', 'main_dir': currentFolder, 'user': user, 'serverAddress': serverAddress}}/>}
    </div>
  )
}

export default App;
