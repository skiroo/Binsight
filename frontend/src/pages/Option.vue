<template>
  <div class="rule-groups-page">
    <h1>{{ lang === 'fr' ? 'Gestion des groupes de règles' : 'Rule Groups Management' }}</h1>

    <form @submit.prevent="onAddGroup" class="add-group-form">
      <h2>{{ lang === 'fr' ? 'Ajouter un groupe' : 'Add a Group' }}</h2>
      <input
        type="text"
        v-model="newGroup.nom"
        :placeholder="lang === 'fr' ? 'Nom du groupe' : 'Group name'"
        required
      />
      <textarea
        v-model="newGroup.description"
        :placeholder="lang === 'fr' ? 'Description' : 'Description'"
      ></textarea>
      <button type="submit">{{ lang === 'fr' ? 'Ajouter' : 'Add' }}</button>
    </form>

    <div class="groups-list" v-if="groups.length">
      <h2>{{ lang === 'fr' ? 'Groupes existants' : 'Existing Groups' }}</h2>
      <ul>
        <li v-for="group in groups" :key="group.id">
          <strong>{{ group.nom }}</strong>
          <p>{{ group.description || (lang === 'fr' ? 'Pas de description' : 'No description') }}</p>

          <button @click="editGroup(group)">{{ lang === 'fr' ? 'Modifier' : 'Edit' }}</button>
          <button @click="deleteGroup(group.id)">{{ lang === 'fr' ? 'Supprimer' : 'Delete' }}</button>
        </li>
      </ul>
    </div>

    <div v-if="editingGroup" class="edit-group-modal">
      <h2>{{ lang === 'fr' ? 'Modifier le groupe' : 'Edit Group' }}</h2>
      <input
        type="text"
        v-model="editingGroup.nom"
        :placeholder="lang === 'fr' ? 'Nom du groupe' : 'Group name'"
        required
      />
      <textarea
        v-model="editingGroup.description"
        :placeholder="lang === 'fr' ? 'Description' : 'Description'"
      ></textarea>
      <button @click="updateGroup">{{ lang === 'fr' ? 'Enregistrer' : 'Save' }}</button>
      <button @click="cancelEdit">{{ lang === 'fr' ? 'Annuler' : 'Cancel' }}</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getRuleGroups, addRuleGroup, updateRuleGroup, deleteRuleGroup } from '@/services/api'

const props = defineProps({ lang: String })

const groups = ref([])
const newGroup = ref({ nom: '', description: '' })
const editingGroup = ref(null)

async function loadGroups() {
  try {
    const res = await getRuleGroups()
    groups.value = res.data
  } catch (err) {
    console.error('Erreur chargement groupes:', err)
  }
}

async function onAddGroup() {
  if (!newGroup.value.nom.trim()) return
  try {
    await addRuleGroup(newGroup.value)
    newGroup.value.nom = ''
    newGroup.value.description = ''
    await loadGroups()
  } catch (err) {
    console.error('Erreur ajout groupe:', err)
  }
}

function editGroup(group) {
  editingGroup.value = { ...group } // clone
}

function cancelEdit() {
  editingGroup.value = null
}

async function updateGroup() {
  if (!editingGroup.value.nom.trim()) return
  try {
    await updateRuleGroup(editingGroup.value.id, {
      nom: editingGroup.value.nom,
      description: editingGroup.value.description
    })
    editingGroup.value = null
    await loadGroups()
  } catch (err) {
    console.error('Erreur mise à jour groupe:', err)
  }
}

async function deleteGroup(id) {
  if (!confirm(props.lang === 'fr' ? 'Confirmer la suppression ?' : 'Confirm delete?')) return
  try {
    await deleteRuleGroup(id)
    await loadGroups()
  } catch (err) {
    console.error('Erreur suppression groupe:', err)
  }
}

onMounted(() => {
  loadGroups()
})
</script>

<style scoped>
.rule-groups-page {
  max-width: 600px;
  margin: auto;
  padding: 1rem;
}
.add-group-form input,
.add-group-form textarea {
  width: 100%;
  margin-bottom: 8px;
  padding: 6px;
  border-radius: 4px;
  border: 1px solid #ccc;
}
.add-group-form button {
  padding: 8px 12px;
  background-color: #16a085;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
.groups-list ul {
  list-style: none;
  padding: 0;
}
.groups-list li {
  border: 1px solid #ddd;
  border-radius: 6px;
  padding: 12px;
  margin-bottom: 10px;
  background: #f9f9f9;
}
.groups-list button {
  margin-right: 10px;
  padding: 6px 10px;
  cursor: pointer;
}
.edit-group-modal {
  position: fixed;
  top: 20%;
  left: 50%;
  transform: translateX(-50%);
  background: white;
  padding: 1rem 2rem;
  border-radius: 8px;
  box-shadow: 0 0 10px rgba(0,0,0,0.25);
  max-width: 400px;
  width: 90%;
}
.edit-group-modal input,
.edit-group-modal textarea {
  width: 100%;
  margin-bottom: 10px;
  padding: 6px;
  border-radius: 4px;
  border: 1px solid #ccc;
}
.edit-group-modal button {
  margin-right: 10px;
  padding: 8px 12px;
  cursor: pointer;
}
</style>
