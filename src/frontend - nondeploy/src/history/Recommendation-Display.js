import React from 'react';

export default function RecommendationDisplay(props) {
    const displayScores = (props) => {
        const {scores} = props;

        if (scores.length >0){
            return (
             scores.map((score, index) => {
                  console.log(score);
                  return (
                      <div>
                          <h3>{score.score}</h3>
                          <h3>{score.browser_score}</h3>
                          <h3>{score.face_score}</h3>
                      </div>

                )
            })
        )
        } else {
            return (<h3>No scores yet</h3>)
        }

    }
    return (
        <>
            {displayScores(props)}
        </>
    )
}