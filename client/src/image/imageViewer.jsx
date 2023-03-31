import React, { useState, useEffect} from 'react'
import axios from 'axios';
import './imageViewer.css'
const cross = require('../cross.png');


const ImageViewer = function(props){
    const [images, setImages] = useState([]);
    const [visible, setVisible] = useState(false);
    const [currentImg, setCurrentImg] = useState();

    console.log(props.props['thumbnail_dir'])
    console.log(props['thumbnail_dir'])

    const thumbnail_dir = props.props['thumbnail_dir']
    const main_dir = props.props['main_dir']
    const user = props.props['user']
    const serverAddress = props.props['serverAddress']

    const listdir = () => {
        var query = `${serverAddress}/get_liked/${user}`
        console.log(query)
        axios.get(query).then((response) => {
            setImages(response.data);
        });
    }

    const close = function(visible){
        setVisible(false)
        console.log('pressed')
    }

    const open = function(img){
        setCurrentImg(img.replace(thumbnail_dir, main_dir))
        setVisible(true)
    }

    useEffect(() => {
        listdir();
      }, []);

    return (
        <div>
            <div id="main_container" style={{position: 'absolute', top: '100px'}}>
                {images.map((img, index) => 
                    <img src={img} 
                    key={index} 
                    onClick={() => {open(img)}}
                    className="ImageViewer_image"
                />
                )}
            </div>

            {visible && <div id="image_container">
                <img id="image_view" src={currentImg}/>
                <img src={String(cross)} id="close_button" onClick={() => {setVisible(false)}}/>
            </div>}
        </div>
    )
}

export default ImageViewer;
