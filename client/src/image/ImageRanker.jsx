import React, { useState, useEffect } from 'react'
import axios from 'axios';
import './ImageRanker.css'

const ImageRanker = function(props){
    const [imgSrc, setImgSrc] = useState('');
    const user = props.props['user']
    const serverAddress = props.props['serverAddress']
    console.log(serverAddress)

    const get_image = () => {
        var query = `${serverAddress}/get_last/${user}`
        axios.get(query).then((response) => {
            setImgSrc(response.data);
        });
    }

    useEffect(() => {
        get_image();
      }, []);


    const onlike = (image) => {
        axios.get(`${serverAddress}/like/${user}/${image.pop()}`).then(
            data => {
            setImgSrc(data.data)
        })
    }

    const ondislike = (image) => {
        axios.get(`${serverAddress}/dislike/${user}/${image.pop()}`).then(
            data => {
            setImgSrc(data.data)
        })
    }

    let maxWidth = '300px'
    let maxHeight = '380px'


    if(window.innerWidth >= 600)
    {
        maxWidth = `${window.innerWidth - 200}px`
        maxHeight = `${window.innerHeight - 300}px`
    }
    console.log(maxWidth)

    return (
        <div>
            <div id="like_image_container">
                <img src={imgSrc} id="like_image" style={{maxWidth: maxWidth, maxHeight: maxHeight}}/>
                <div id="btn_container">
                    <button id="like_button" onClick={()=>{onlike(imgSrc.split('/'))}}>Like</button>
                    <button id="dislike_button" onClick={()=>{ondislike(imgSrc.split('/'))}}>Disike</button>
                </div>
            </div>
        </div>
    )
}

export default ImageRanker;

