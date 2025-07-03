<template>
  <div class="upload-container">
    <h2>Envoyer une image</h2>

    <!-- Sélection ou capture d’image -->
    <input type="file" accept="image/*" @change="handleFileChange" />
    <button @click="useCamera">Prendre une photo</button>
    <video ref="video" autoplay playsinline style="display:none;" width="300"></video>
    <canvas ref="canvas" style="display:none;"></canvas>

    <!-- Choix du mode -->
    <label>Mode de classification :</label>
    <select v-model="mode">
      <option value="auto">Automatique</option>
      <option value="manuel">Manuel</option>
      <option value="ia">IA (bientôt)</option>
    </select>

    <!-- Bouton d’envoi -->
    <button @click="submitImage" :disabled="!imageBlob">Envoyer</button>

    <!-- Résultat -->
    <div v-if="uploadResult">
      <h3>Résultat :</h3>
      <p>Classification : {{ uploadResult.classification_auto }}</p>
      <img :src="previewUrl" style="max-width: 300px;" />

      <div v-if="!annotationSent">
        <p>Annoter manuellement :</p>
        <button @click="annotate('dirty')">Pleine</button>
        <button @click="annotate('clean')">Vide</button>
      </div>
      <p v-if="annotationMsg">{{ annotationMsg }}</p>
    </div>
  </div>
</template>

<script>
    export default {
        data() {
            return {
                mode: 'auto',
                imageBlob: null,
                previewUrl: '',
                uploadResult: null,
                annotationSent: false,
                annotationMsg: '',
            };
        },

        methods: {
            handleFileChange(e) {
                const file = e.target.files[0];
                if (file) {
                    this.imageBlob = file;
                    this.previewUrl = URL.createObjectURL(file);
                }
            },

            useCamera() {
                const video = this.$refs.video;
                video.style.display = 'block';

                navigator.mediaDevices.getUserMedia({ video: true }).then(stream => {
                    video.srcObject = stream;

                    setTimeout(() => {
                        this.capturePhoto();
                        stream.getTracks().forEach(track => track.stop());
                        video.style.display = 'none';
                    }, 3000);
                });
            },
            capturePhoto() {
                const video = this.$refs.video;
                const canvas = this.$refs.canvas;
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;

                const ctx = canvas.getContext('2d');
                ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

                canvas.toBlob(blob => {
                    this.imageBlob = blob;
                    this.previewUrl = URL.createObjectURL(blob);
                }, 'image/jpeg');
            },

            async submitImage() {
                const formData = new FormData();
                formData.append('image', this.imageBlob);
                formData.append('mode_classification', this.mode);

                try {
                    const res = await fetch('http://localhost:5000/upload', {
                        method: 'POST',
                        body: formData,
                    });

                    const data = await res.json();
                    this.uploadResult = data;
                    this.annotationSent = false;

                    // Localisation automatique si capture
                    if (navigator.geolocation) {
                        navigator.geolocation.getCurrentPosition(pos => {
                            console.log('Géolocalisation :', pos.coords.latitude, pos.coords.longitude);
                            // TODO : envoyer localisation vers /localisation plus tard
                        });
                    }
                } catch (err) {
                    console.error('Erreur upload :', err);
                }
            },

            async annotate(etat) {
                try {
                    const res = await fetch(`http://localhost:5000/annotate/${this.uploadResult.image_id}`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ etat }),
                    });
                    const data = await res.json();
                    this.annotationMsg = data.message;
                    this.annotationSent = true;
                } catch (err) {
                    this.annotationMsg = "Erreur lors de l'annotation";
                }
            },
        },
    };
</script>
