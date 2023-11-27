import React from 'react';
import '../styles/App.css';
import Box from '../components/Box';
import { useLocation } from 'react-router-dom/cjs/react-router-dom.min';


const Search = () => {
    const location = useLocation();
    const recommendationData = location.search ? JSON.parse(decodeURIComponent(location.search.split('=')[1])) : [];

    console.log('rec:',recommendationData)

    return (
        <>
            <div className="heading-container">
                <h1 className="heading-recommend">Recommended Songs</h1>
            </div>
			<Box random={recommendationData}/>
        </>
    );
};

export default Search;
