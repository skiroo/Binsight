<template>
  <div class="container">
    <!-- -->
    <h2>{{ lang === 'fr' ? 'Clé d\'accès' : 'Acces Key' }}</h2>    

    <div v-if="role === 'admin'" class="box">
        <h3>{{ lang === 'fr' ? 'Clé d’inscription agent' : 'Agent Signup Key' }}</h3>
        <button @click="createAgentKey" class="btn btn-green">
            {{ lang === 'fr' ? 'Générer une clé' : 'Generate a key' }}
        </button>
        <p v-if="generatedKey" class="generated-key">
            {{ lang === 'fr' ? 'Clé générée :' : 'Generated key:' }} <strong>{{ generatedKey }}</strong>
        </p>
    </div>

    <div v-if="role === 'admin'" class="box">
        <h3>{{ lang === 'fr' ? 'Clés existantes' : 'Existing Keys' }}</h3>
        <table>
            <thead>
                <tr>
                    <th>{{ lang === 'fr' ? 'Clé' : 'Key' }}</th>
                    <th>{{ lang === 'fr' ? 'Active' : 'Active' }}</th>
                    <th>{{ lang === 'fr' ? 'Actions' : 'Actions' }}</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="cle in accessKeys" :key="cle.id">
                    <td style="word-break: break-all">{{ cle.cle }}</td>
                    <td class="center">
                    <input type="checkbox" :checked="cle.valide" @change="toggleKeyStatus(cle)" />
                    </td>
                    <td>
                    <button @click="removeKey(cle)" class="link red">{{ lang === 'fr' ? 'Supprimer' : 'Delete' }}</button>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>

    <hr>

    <h2>{{ lang === 'fr' ? 'Gestion des Règles' : 'Rule Management' }}</h2>

    <!-- Formulaire groupe -->
    <div class="box">
      <h3>
        {{ editingGroupId
          ? lang === 'fr' ? 'Modifier le groupe' : 'Edit Group'
          : lang === 'fr' ? 'Ajouter un groupe' : 'Add Group'
        }}
      </h3>
      <input v-model="newGroup.nom" :placeholder="lang === 'fr' ? 'Nom du groupe' : 'Group name'" class="input" />
      <input v-model="newGroup.description" :placeholder="lang === 'fr' ? 'Description' : 'Description'" class="input" />
      <button @click="submitGroup" class="btn btn-green">
        {{ editingGroupId ? (lang === 'fr' ? 'Mettre à jour' : 'Update') : (lang === 'fr' ? 'Ajouter' : 'Add') }}
      </button>
      <button v-if="editingGroupId" @click="cancelEditGroup" class="btn btn-cancel">
        {{ lang === 'fr' ? 'Annuler' : 'Cancel' }}
      </button>
    </div>

    <!-- Sélecteur de groupe -->
    <div class="selector">
      <label>{{ lang === 'fr' ? 'Sélectionner un groupe :' : 'Select a group:' }}</label>
      <select v-model="selectedGroupId" @change="fetchRules">
        <option disabled value="">{{ lang === 'fr' ? '-- Choisir un groupe --' : '-- Choose a group --' }}</option>
        <option v-for="group in groups" :key="group.id" :value="group.id">
          {{ group.nom }}
        </option>
      </select>
    </div>

    <!-- Table des groupes -->
    <table>
      <thead>
        <tr>
          <th>{{ lang === 'fr' ? 'Nom' : 'Name' }}</th>
          <th>{{ lang === 'fr' ? 'Description' : 'Description' }}</th>
          <th>{{ lang === 'fr' ? 'Actions' : 'Actions' }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="group in groups" :key="group.id">
          <td>{{ group.nom }}</td>
          <td>{{ group.description }}</td>
          <td>
            <button @click="editGroup(group)" class="link green">{{ lang === 'fr' ? 'Modifier' : 'Edit' }}</button>
            <button @click="removeGroup(group.id)" class="link red">{{ lang === 'fr' ? 'Supprimer' : 'Delete' }}</button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- Règles -->
    <div v-if="selectedGroupId">
      <h2>{{ lang === 'fr' ? 'Règles du groupe sélectionné' : 'Rules in selected group' }}</h2>

      <!-- Ajout règle -->
      <div class="box">
        <input v-model="newRule.nom" :placeholder="lang === 'fr' ? 'Nom' : 'Name'" class="input" />
        <input v-model="newRule.condition" :placeholder="lang === 'fr' ? 'Condition logique' : 'Logic condition'" class="input" />
        <input v-model="newRule.description" :placeholder="lang === 'fr' ? 'Description' : 'Description'" class="input" />
        <button @click="addRule" class="btn btn-green">{{ lang === 'fr' ? 'Ajouter' : 'Add' }}</button>
      </div>

      <!-- Liste des règles -->
      <table>
        <thead>
          <tr>
            <th>{{ lang === 'fr' ? 'Nom' : 'Name' }}</th>
            <th>{{ lang === 'fr' ? 'Condition' : 'Condition' }}</th>
            <th>{{ lang === 'fr' ? 'Active' : 'Active' }}</th>
            <th>{{ lang === 'fr' ? 'Actions' : 'Actions' }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="rule in rules" :key="rule.id">
            <td>{{ rule.nom }}</td>
            <td>{{ rule.condition }}</td>
            <td class="center">
              <input type="checkbox" v-model="rule.active" @change="toggleRuleActive(rule)" />
            </td>
            <td>
              <button @click="removeRule(rule.id)" class="link red">{{ lang === 'fr' ? 'Supprimer' : 'Delete' }}</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <hr>

    <div class="export-section">
      <h2>{{ lang === 'fr' ? 'Exporter des données personnalisées' : 'Export custom data' }}</h2>

      <label>{{ lang === 'fr' ? 'Filtres de date :' : 'Date filters:' }}</label>
      <input type="date" v-model="filters.dateMin" />
      <input type="date" v-model="filters.dateMax" />

      <label><b>{{ lang === 'fr' ? 'État' : 'Status' }} :</b></label>
      <div class="etat-filters">
        <button :class="{ active: filters.etat === '' }" @click="filters.etat = ''">{{ lang === 'fr' ? 'Tous' : 'All' }}</button>
        <button :class="{ active: filters.etat === 'clean' }" @click="filters.etat = 'clean'">{{ lang === 'fr' ? 'Propres' : 'Clean' }}</button>
        <button :class="{ active: filters.etat === 'dirty' }" @click="filters.etat = 'dirty'">{{ lang === 'fr' ? 'Pleines' : 'Full' }}</button>
      </div>

      <label><b>{{ lang === 'fr' ? 'Source' : 'Source' }} :</b></label>
      <div class="etat-filters">
        <button :class="{ active: filters.source === '' }" @click="filters.source = ''">{{ lang === 'fr' ? 'Toutes' : 'All' }}</button>
        <button :class="{ active: filters.source === 'citoyen' }" @click="filters.source = 'citoyen'">{{ lang === 'fr' ? 'Citoyen' : 'Citizen' }}</button>
        <button :class="{ active: filters.source === 'agent' }" @click="filters.source = 'agent'">{{ lang === 'fr' ? 'Agent' : 'Agent' }}</button>
        <button :class="{ active: filters.source === 'caméra' }" @click="filters.source = 'caméra'">{{ lang === 'fr' ? 'Caméra' : 'Camera' }}</button>
      </div>

      <label><b>{{ lang === 'fr' ? 'Quartier :' : 'District:' }}</b></label>
      <div class="quartier-wrapper">
        <input type="text" v-model="quartierInput" :placeholder="lang === 'fr' ? 'Ex : 13e' : 'e.g. 13th'" @input="updateQuartierSuggestions" @focus="updateQuartierSuggestions" @blur="hideSuggestionsWithDelay" />
        <ul v-if="showSuggestions" class="suggestion-list">
          <li v-for="q in quartierSuggestions" :key="q" @mousedown.prevent="selectQuartierSuggestion(q)">{{ q }}</li>
        </ul>
      </div>

      <button class="btn" style="margin-top: 1rem" @click="resetFilters">{{ lang === 'fr' ? 'Réinitialiser les filtres' : 'Reset filters' }}</button>

      <label>{{ lang === 'fr' ? 'Tables à inclure :' : 'Tables to include:' }}</label>
      <div class="checkboxes">
        <label><input type="checkbox" v-model="tables.image" /> {{ lang === 'fr' ? 'Image' : 'Image' }}</label>
        <label><input type="checkbox" v-model="tables.caracteristiques" /> {{ lang === 'fr' ? 'Caractéristiques' : 'Features' }}</label>
        <label><input type="checkbox" v-model="tables.localisation" /> {{ lang === 'fr' ? 'Localisation' : 'Location' }}</label>
        <label><input type="checkbox" v-model="tables.utilisateur" /> {{ lang === 'fr' ? 'Utilisateur' : 'User' }}</label>
      </div>

      <button @click="exportCustom" class="btn-export">
        {{ lang === 'fr' ? 'Télécharger le CSV' : 'Download CSV' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import {
  getRuleGroups, addRuleGroup, updateRuleGroup, deleteRuleGroup,
  getRulesByGroup, addRuleToGroup, deleteRule, updateRule,
  generateAgentKey, getAccessKeys, updateAccessKey, deleteAccessKey,
  getLocalisations
} from '../services/api';

const { lang } = defineProps({ lang: String });
const role = localStorage.getItem('role');

const groups = ref([]);
const rules = ref([]);
const selectedGroupId = ref('');
const newGroup = ref({ nom: '', description: '' });
const editingGroupId = ref(null);
const newRule = ref({ nom: '', condition: '', description: '' });
const generatedKey = ref('');
const accessKeys = ref([]);

const quartierInput = ref('');
const showSuggestions = ref(false);
const quartierSuggestions = ref([]);
const allQuartiers = ref([]);

const filters = ref({
  dateMin: '',
  dateMax: '',
  etat: '',
  source: '',
  quartier: ''
});

const tables = ref({
  image: true,
  caracteristiques: true,
  localisation: false,
  utilisateur: false
});

// 📥 Export CSV personnalisé
function exportCustom() {
  const params = new URLSearchParams();
  const selectedTables = Object.entries(tables.value)
    .filter(([_, v]) => v)
    .map(([k]) => k);
  params.append('tables', selectedTables.join(','));
  Object.entries(filters.value).forEach(([key, value]) => {
    if (value) params.append(key, value);
  });
  window.open(`http://localhost:5000/export/custom?${params.toString()}`, '_blank');
}

// ♻️ Réinitialisation des filtres export
function resetFilters() {
  filters.value = {
    dateMin: '',
    dateMax: '',
    etat: '',
    source: '',
    quartier: ''
  };
  quartierInput.value = '';
}

// 🔍 Suggestions de quartier
function updateQuartierSuggestions() {
  const input = quartierInput.value.toLowerCase();
  quartierSuggestions.value = allQuartiers.value
    .filter(q => q.toLowerCase().includes(input))
    .slice(0, 10);
  showSuggestions.value = quartierInput.value.length >= 2;
}

function selectQuartierSuggestion(q) {
  quartierInput.value = q;
  filters.value.quartier = q;
  showSuggestions.value = false;
}

function hideSuggestionsWithDelay() {
  setTimeout(() => {
    showSuggestions.value = false;
  }, 150);
}

// 🔑 Gestion des clés d'accès
async function createAgentKey() {
  try {
    const res = await generateAgentKey();
    generatedKey.value = res.data.cle;
  } catch {
    alert(lang === 'fr' ? "Erreur lors de la génération." : "Generation error.");
  }
}

async function fetchAccessKeys() {
  try {
    const res = await getAccessKeys();
    accessKeys.value = res.data;
  } catch {
    alert(lang === 'fr' ? "Erreur lors du chargement des clés." : "Error loading keys.");
  }
}

async function toggleKeyStatus(cle) {
  await updateAccessKey(cle.id, { valide: !cle.valide });
  await fetchAccessKeys();
}

async function removeKey(cle) {
  if (confirm(lang === 'fr' ? "Supprimer cette clé ?" : "Delete this key?")) {
    await deleteAccessKey(cle.id);
    await fetchAccessKeys();
  }
}

// 📦 Groupes de règles
async function fetchGroups() {
  const res = await getRuleGroups();
  groups.value = res.data;
}

async function fetchRules() {
  if (!selectedGroupId.value) return;
  const res = await getRulesByGroup(selectedGroupId.value);
  rules.value = res.data;
}

async function submitGroup() {
  if (!newGroup.value.nom) return;
  if (editingGroupId.value) {
    await updateRuleGroup(editingGroupId.value, newGroup.value);
  } else {
    await addRuleGroup(newGroup.value);
  }
  newGroup.value = { nom: '', description: '' };
  editingGroupId.value = null;
  await fetchGroups();
}

function editGroup(group) {
  newGroup.value = { nom: group.nom, description: group.description };
  editingGroupId.value = group.id;
}

function cancelEditGroup() {
  newGroup.value = { nom: '', description: '' };
  editingGroupId.value = null;
}

async function removeGroup(id) {
  if (confirm(lang === 'fr' ? "Supprimer ce groupe avec ses règles ?" : "Delete this group and its rules?")) {
    await deleteRuleGroup(id);
    if (selectedGroupId.value === id) {
      selectedGroupId.value = '';
      rules.value = [];
    }
    await fetchGroups();
  }
}

// 🧠 Règles
async function addRule() {
  if (!newRule.value.nom || !newRule.value.condition) return;
  await addRuleToGroup(selectedGroupId.value, newRule.value);
  newRule.value = { nom: '', condition: '', description: '' };
  await fetchRules();
}

async function removeRule(id) {
  if (confirm(lang === 'fr' ? "Supprimer cette règle ?" : "Delete this rule?")) {
    await deleteRule(id);
    await fetchRules();
  }
}

async function toggleRuleActive(rule) {
  await updateRule(rule.id, { active: rule.active });
}

// 🏁 Initialisation
onMounted(async () => {
  fetchGroups();
  if (role === 'admin') fetchAccessKeys();

  const res = await getLocalisations();
  const raw = res.data.map(p => p.quartier || p.ville || '').filter(Boolean);
  allQuartiers.value = [...new Set(raw)].sort();
});
</script>

<style scoped>
.container {
  padding: 2rem;
  max-width: 1100px;
  margin: auto;
  font-family: sans-serif;
}

h2 {
  font-size: 1.5rem;
  font-weight: bold;
  margin-bottom: 1rem;
}
h3 {
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.box {
  background: #f9f9f9;
  padding: 1rem;
  border-radius: 0.5rem;
  margin-bottom: 1.5rem;
}

.input {
  border: 1px solid #ccc;
  padding: 0.5rem;
  margin-right: 0.5rem;
  margin-bottom: 0.5rem;
  width: 250px;
}

.selector {
  margin-bottom: 1rem;
}

.btn {
  padding: 0.5rem 1rem;
  margin-top: 0.5rem;
  border-radius: 0.25rem;
  cursor: pointer;
}

.btn-green {
  background-color: #10b981;
  color: white;
}

.btn-cancel {
  background-color: transparent;
  color: #dc2626;
  border: none;
  margin-left: 1rem;
}

.link {
  cursor: pointer;
  font-size: 0.9rem;
  border: none;
  background: none;
}

.green {
  color: #10b981;
}
.red {
  color: #dc2626;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 2rem;
}
th,
td {
  border: 1px solid #ddd;
  padding: 0.5rem;
}
thead {
  background-color: #f3f4f6;
}
.center {
  text-align: center;
}

/* 🔒 Clés */
.generated-key {
  margin-top: 0.5rem;
  font-weight: bold;
  color: red;
  word-break: break-word;
}

/* 📤 Export */
.export-section {
  background: #f9f9f9;
  padding: 1rem;
  border-radius: 0.5rem;
  margin-top: 2rem;
  margin-bottom: 2rem;
}
.export-section h2 {
  font-size: 1.5rem;
  font-weight: bold;
  margin-bottom: 1rem;
}
.export-section label {
  display: block;
  margin-top: 0.75rem;
  margin-bottom: 0.25rem;
  font-weight: 500;
}
.export-section input[type="date"],
.export-section input[type="text"],
.export-section select {
  padding: 0.5rem;
  margin-right: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 0.25rem;
  width: 250px;
  margin-bottom: 0.5rem;
}
.export-section input[type="checkbox"] {
  margin-right: 0.5rem;
}
.export-section .checkboxes {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-top: 0.5rem;
}
.export-section .btn-export {
  margin-top: 1rem;
  background-color: #10b981;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 0.25rem;
  cursor: pointer;
  transition: background-color 0.2s ease;
}
.export-section .btn-export:hover {
  background-color: #059669;
}

/* 🔘 Filtres horizontaux */
.etat-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-top: 0.5rem;
  margin-bottom: 1rem;
}
.etat-filters button {
  padding: 0.4rem 1rem;
  border: 1px solid #ccc;
  background-color: white;
  border-radius: 0.25rem;
  cursor: pointer;
  transition: all 0.2s ease;
  font-weight: 500;
}
.etat-filters button.active {
  background-color: #10b981;
  color: white;
  border-color: #10b981;
}
.etat-filters button:hover {
  background-color: #f0fdf4;
  border-color: #10b981;
}

/* 📍 Suggestions quartier */
.quartier-wrapper {
  position: relative;
  z-index: 100;
}
.suggestion-list {
  list-style: none;
  padding: 0;
  margin: 2px 0 0;
  border: 1px solid #ccc;
  border-radius: 6px;
  background-color: white;
  color: black;
  max-height: 200px;
  overflow-y: auto;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  position: absolute;
  width: 250px;
  z-index: 200;
}
.suggestion-list li {
  padding: 8px 10px;
  cursor: pointer;
  transition: background-color 0.2s;
}
.suggestion-list li:hover {
  background-color: #f0fdf4;
  font-weight: bold;
}

/* 🌙 Mode sombre */
.dark-theme .box,
.dark-theme .export-section {
  background-color: #1f2937;
  color: #f1f1f1;
}
.dark-theme thead {
  background-color: #374151;
  color: #f1f1f1;
}
.dark-theme table {
  border-color: #444;
}
.dark-theme th,
.dark-theme td {
  border-color: #444;
}
.dark-theme input,
.dark-theme select {
  background-color: #374151;
  color: #f1f1f1;
  border-color: #555;
}
.dark-theme .suggestion-list {
  background-color: #374151;
  color: white;
  border-color: #555;
}
.dark-theme .btn-export,
.dark-theme .etat-filters button.active {
  background-color: #10b981;
  color: #fff;
}
.dark-theme .etat-filters button {
  background-color: #374151;
  color: #f1f1f1;
  border-color: #555;
}
.dark-theme .etat-filters button:hover {
  background-color: #1f2937;
}
</style>