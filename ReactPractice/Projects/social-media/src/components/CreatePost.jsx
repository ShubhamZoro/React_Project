import { useRef, useContext } from "react";
import { PostList } from "../store/post-list-store";
function CreatePost() {
  const { addPost } = useContext(PostList);
  const userId = useRef();
  const postTitle = useRef();
  const postBody = useRef();
  const reactions = useRef();
  const tags = useRef();

  const handleSubmit = (event) => {
    event.preventDefault();
    const useridvalue = userId.current.value;
    const posttilevalue = postTitle.current.value;
    const postBodyvalue = postBody.current.value;
    const reactionsvalue = reactions.current.value;
    const tagsvalue = tags.current.value.split(" ");
    addPost(
      useridvalue,
      posttilevalue,
      postBodyvalue,
      reactionsvalue,
      tagsvalue
    );
    userId.current.value = "";
    postTitle.current.value = "";
    postBody.current.value = "";
    reactions.current.value = "";
    tags.current.value = "";
  };

  return (
    <form className="create-post" onSubmit={handleSubmit}>
      <div className="mb-3">
        <label htmlFor="userId" className="form-label">
          Enter your User Id here
        </label>
        <input
          type="text"
          className="form-control"
          id="id"
          ref={userId}
          placeholder="Enter Id here"
        />
      </div>
      <div className="mb-3">
        <label htmlFor="title" className="form-label">
          Post Title
        </label>
        <input
          type="text"
          className="form-control"
          id="title"
          ref={postTitle}
          placeholder="How are you feeling today..."
        />
      </div>

      <div className="mb-3">
        <label htmlFor="title" className="form-label">
          Post Content
        </label>
        <textarea
          type="text"
          rows="4"
          className="form-control"
          id="title"
          ref={postBody}
          placeholder="Tell us about it"
        />
      </div>

      <div className="mb-3">
        <label htmlFor="reactions" className="form-label">
          Number of reactions
        </label>
        <input
          type="text"
          className="form-control"
          id="reactions"
          ref={reactions}
          placeholder="How many people reacted to this post"
        />
      </div>

      <div className="mb-3">
        <label htmlFor="tags" className="form-label">
          Enter your tags
        </label>
        <input
          type="text"
          className="form-control"
          id="tags"
          ref={tags}
          placeholder="Please enter tags with space"
        />
      </div>

      <button type="submit" className="btn btn-primary">
        Submit
      </button>
    </form>
  );
}

export default CreatePost;
