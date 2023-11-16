import { useState } from 'react';
import axios from 'axios';
import { Button, Label, TextInput } from 'flowbite-react';
import ImageGallery from './ImageGallery.jsx';

function App() {
  const [songName, setSongName] = useState('');
  const [artistName, setArtistName] = useState('');
  const [responseData, setResponseData] = useState(null);

  const handleSubmit = async (event) => {
    event.preventDefault();

    try {
      const response = await axios.get(`http://127.0.0.1:5000/${songName}/${artistName}`);

      setResponseData(response.data);
    } catch (error) {
      console.error('Error submitting the form:', error);
    }
  };

  return (
    <div className="flex items-center justify-center h-screen flex-col m-8 mt-64">
      <form className="flex max-w-lg flex-col gap-4" onSubmit={handleSubmit}>
        <div>
          <div className="mb-2 block">
            <Label htmlFor="song" value="Song Name" />
          </div>
          <TextInput
            name="song"
            type="text"
            placeholder="Shape of You"
            value={songName}
            onChange={(e) => setSongName(e.target.value)}
            required
          />
        </div>
        <div>
          <div className="mb-2 block">
            <Label htmlFor="artist" value="Artist Name" />
          </div>
          <TextInput
            name="artist"
            type="text"
            placeholder="Ed Sheeran"
            value={artistName}
            onChange={(e) => setArtistName(e.target.value)}
            required
          />
        </div>
        <Button type="submit">Submit</Button>
      </form>

      {responseData && (
        <div className="mt-4">
          <ImageGallery imageUrls={responseData}/>
        </div>
      )}
    </div>
  );
}

export default App;
