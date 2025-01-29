

//
// JS pour le changement de couleur des rectangles canvas lorsque un bouton ou input correspondant est selectionné
//
let previousInput = null; // Variable globale pour suivre l'input précédemment sélectionné

function buttonclick(ctx) {
        if (previousInput) {
            previous_input_id = previousInput.name.split('_')[1]
            var previousobject = canvas.getObjects().find(obj => obj.rectid == input_id);
            previousobject.set('fill', 'rgba(0,0,255,0.1)');
        }
        input_id = ctx.name.split('_')[1]
        var object = canvas.getObjects().find(obj => obj.rectid == input_id);
        if (object) {
          object.set('fill', 'rgba(0,255,0,0.2)');
          canvas.renderAll();
        } else {
          console.error('Object not found.');
        }
        previousInput = ctx;
    }

