export const ImageDisplay = ({text,imageBase64}) => {
    return (
        <h2>
            {text}
            {imageBase64 && <img src={imageBase64} alt="Uploaded" />}
        </h2>
    )
}